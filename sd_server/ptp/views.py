from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django import forms
from models import Jobs
from subprocess import Popen
import subprocess
import os
import logging
from time import sleep
import xml.dom.minidom as minidom

logger = logging.getLogger(__name__)

class PTPForm(forms.Form):
    treefile = forms.FileField(label="""My phylogenetic input tree, 
    if input file contains multiple trees, only the first tree will be used:""")
    rooted = forms.ChoiceField(choices = (("untrooted", "Unrooted"), ("rooted", "Rooted")), label = 'My tree is:',
                                help_text = "If unrooted, the tree will be rooted at the longest branch.")
    #pvalue = forms.DecimalField(label = 'P-value:', initial = 0.001)
    nmcmc = forms.IntegerField(label = "No. MCMC generations:", initial = 100000, max_value = 500000, min_value = 10000,
                                help_text = """For small trees (<50 taxa), 100000 is usually enough, but you should always check for convergence.""")
    imcmc = forms.IntegerField(label = "Thinning:", initial = 100, max_value = 1000, min_value = 100)
    burnin = forms.DecimalField(label = 'Burn-in:', initial = 0.1, max_value = 0.5, min_value = 0.09,
                                help_text = "Always check if more burn-in is needed.")
    seed = forms.IntegerField(label = "Seed:", initial = 123, 
                                help_text = "Change the seed if MCMC chains does not converge.")
    outgroups = forms.CharField(label = "Outgroup taxa names(if any):", required=False, 
                                help_text = "e.g. t1 t2 t3, taxa name separated by a single space, if specified, the tree will be rerooted accordingly." )
    removeog = forms.BooleanField(label = "Remove outgroups(if any):", required=False,
                                help_text = "Remove outgroups that are distant related can improve the delimitation results.")
    sender = forms.EmailField(label='My e-mail address:',
                                help_text = "You can use it to find your results later.")


class jobform(forms.Form):
    job_id = forms.IntegerField(label = "Job id:")
    sender = forms.EmailField(label='E-mail address:')


def index(request):
    frees, totals = server_stats() 
    context = {'available':frees, 'total':totals}
    return render(request, 'index.html', context)


def help1(request):
    context = {}
    return render(request, 'ptp/help.html', context)


def thanks(request):
    return HttpResponse("Thanks for using our service!")


def autherror(request):
    return HttpResponse("Job id does not exists or e-mail address does not match!")

def queue_error(request):
    return HttpResponse("There is something wrong with the computational queue, please try again later!")

def findjob(request):
    if request.method == 'POST': # If the form has been submitted...
        jform = jobform(request.POST)
        if jform.is_valid():
            email = jform.cleaned_data['sender']
            job_id = jform.cleaned_data['job_id']
            jobs = Jobs.objects.filter(id=job_id)
            if len(jobs) > 0:
                if jobs[0].email != email:
                    return autherror(request)
            else:
                return autherror(request)
            out_path = os.path.join( settings.JOB_FOLDER, job_id, "output")
            outpar = os.path.join( settings.JOB_FOLDER, job_id, "output.PTPPartitonSummary.txt")
            outplot = os.path.join( settings.JOB_FOLDER, job_id, "output.PTPhSupportPartition.txt.png")

            frees, totals = server_stats() 
            
            # finished?
            if not os.path.exists(out_path):
                return render(request, 'ptp/results.html', {'result':"Job still running", 'jobid':job_id, 'email':email, 'available':frees, 'total':totals})
            # at least two of the expected output files exists
            if os.path.exists(outpar) and os.path.exists(outplot):
                with open(out_path) as outfile:
                    lines = outfile.readlines()
                    results="<br/>".join(lines)
                    context = {'result':results, 'jobid':job_id, 'email':email}
                    return render(request, 'ptp/results.html', context)
            # the expected output files are not there
            else:
                return render(request, 'ptp/results.html', {'result':"Something is wrong, please check your input file", 'jobid':job_id, 'email':email, 'available':frees, 'total':totals})
    else:
        jform = jobform()
    context = {'jform':jform}
    return render(request, 'ptp/findjob.html', context)


def ptp_index(request):
    frees, totals = server_stats() 
    if request.method == 'POST': # If the form has been submitted...
        ptp_form = PTPForm(request.POST, request.FILES) # A form bound to the POST data
        if ptp_form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            job = Jobs()
            job.email = ptp_form.cleaned_data['sender']
            if ptp_form.cleaned_data['rooted'] == "rooted":
                job.data_type = "rptree"
            else:
                job.data_type = "ptree"
            job.method = "PTP"
            job.save()
            filepath = os.path.join( settings.JOB_FOLDER, str(job.id)) 
            os.mkdir(filepath)
            newfilename = os.path.join(filepath,"input.tre")
            handle_uploaded_file(fin = request.FILES['treefile'] , fout = newfilename)
            job.filepath = filepath
            job.save()
            
            nmcmc = ptp_form.cleaned_data['nmcmc']
            imcmc = ptp_form.cleaned_data['imcmc']
            burnin = ptp_form.cleaned_data['burnin']
            seed = ptp_form.cleaned_data['seed']
            outgroups = ptp_form.cleaned_data['outgroups'].strip()
            #print(outgroups)
            removeog = ptp_form.cleaned_data['removeog']
            
            #os.chmod(filepath, 0777)
            jobok = run_ptp_queue(
                        fin = newfilename,
                        fout = os.path.join(filepath,"output"),
                        rooted = (ptp_form.cleaned_data['rooted'] == "rooted"),
                        nmcmc = nmcmc,
                        imcmc = imcmc,
                        burnin = burnin,
                        seed = seed,
                        outgroup = outgroups,
                        remove = removeog)
            
            #return HttpResponseRedirect('result/') # Redirect after POST
            if jobok:
                return show_ptp_result(request, job_id = str(job.id), email = job.email)
            else:
                return queue_error(request)
    else:
        ptp_form = PTPForm() # An unbound form
    context = {'pform':ptp_form, 'available':frees, 'total':totals}
    return render(request, 'ptp/index.html', context)


def show_ptp_result(request, job_id = "", email = ""):
    if job_id == "" or email == "":
        job_id = request.GET.get('job_id', '')
        email = request.GET.get('email', '')
    
    jobs = Jobs.objects.filter(id=job_id)
    if len(jobs) > 0:
        if jobs[0].email != email:
            return autherror(request)
    else:
        return autherror(request)
    
    out_path = os.path.join( settings.JOB_FOLDER, job_id, "output")
    outpar = os.path.join( settings.JOB_FOLDER, job_id, "output.PTPPartitonSummary.txt")
    outplot = os.path.join( settings.JOB_FOLDER, job_id, "output.PTPhSupportPartition.txt.png")
    
    frees, totals = server_stats() 
    
    # finished?
    if not os.path.exists(out_path):
        return render(request, 'ptp/results.html', {'result':"Job still running", 'jobid':job_id, 'email':email, 'available':frees, 'total':totals})
    # at least two of the expected output files exists
    if os.path.exists(outpar) and os.path.exists(outplot):
        with open(out_path) as outfile:
            lines = outfile.readlines()
            results="<br/>".join(lines)
            context = {'result':results, 'jobid':job_id, 'email':email}
            return render(request, 'ptp/results.html', context)
    # the expected output files are not there
    else:
        return render(request, 'ptp/results.html', {'result':"Something is wrong, please check your input file", 'jobid':job_id, 'email':email, 'available':frees, 'total':totals})


def show_phylomap_result(request):
    job_id = request.GET.get('job_id', '')
    out_path_line = os.path.join( settings.JOB_FOLDER, job_id, "output.phylomap.line.txt")
    out_path_var = os.path.join( settings.JOB_FOLDER, job_id, "output.phylomap.var")
    context = {'jobid':job_id}
    if os.path.exists(out_path_line):
        if os.path.exists(out_path_var):
            with open(out_path_var) as outfile:
                lines = outfile.readlines()
                results="<br/>".join(lines)
            context['result'] = results
        return render(request, 'ptp/phylomap.html', context)
    else:
        return HttpResponse("PhyloMap result does not exist, please re-submit your job!")


def handle_uploaded_file(fin, fout):
    with open(fout, 'w+') as destination:
        for chunk in fin.chunks():
            destination.write(chunk)


def assemble_command(fin, fout, nmcmc, imcmc, burnin, seed, outgroup, remove, rooted):
    command = ["python", settings.PTP_PY]
    #input and output
    command.extend(["-t", fin,"-o", fout])
    #seed
    command.extend(["-s", str(seed)])
    #options
    command.extend(["-i", str(nmcmc), "-n", str(imcmc), "-b", str(burnin)])
    if outgroup != "":
        command.extend(["-g", outgroup])
        if remove:
            command.append("-d")
    elif not rooted:
        command.append("-r")
    command.extend(["-k", "1"])
    
    # end
    return command

def run_ptp(fin, fout, nmcmc, imcmc, burnin, seed, outgroup = "" , remove = False,  rooted = False):
    command = assemble_command(fin, fout, nmcmc, imcmc, burnin, seed, outgroup, remove, rooted)
    command.insert(0, "nohup")
    Popen( command, stdout=open(fout, "w"), stderr=open(fout+".err", "w"))

def run_ptp_queue(fin, fout, nmcmc, imcmc, burnin, seed, outgroup = "" , remove = False,  rooted = False):
    command = assemble_command(fin, fout, nmcmc, imcmc, burnin, seed, outgroup, remove, rooted)
    
    pbs_script = generate_pbs_script(scommand = " ".join(command), fout = fout)
    jobok = job_submission(fscript = pbs_script)

    return jobok


def server_stats():
    #return free nodes and total number of nodes
    try: 
        p1 = Popen(['pbsnodes', '-x'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        dom = minidom.parseString( p1.communicate()[0])
        node_states = dom.getElementsByTagName("state")
        free = 0
        for state in node_states:
            if state.childNodes[0].data == "free":
                free += 1

        return free, len(node_states)
    except Exception as e:
        logger.error('error in server_stats ' + str(e))
    return 0, 0


def generate_pbs_script(scommand, fout):
    filename = fout+".pbs.sh"
    host = ""
    if( settings.QUEUE_SERVER != ""):
        host += settings.QUEUE_SERVER+":"
    
    with open(filename, "w") as fsh:
        fsh.write("#!/bin/bash\n"
                  "#PBS -S /bin/bash\n"
                  "#PBS -o "+ host + fout + "\n"
                  "#PBS -e "+ host + fout + ".err \n"
                  "#PBS -W umask=022\n\n" # readable by group and all also
        #https://gist.github.com/tyleramos/3744901
                  "SERVERNUM=99\n"
                  "find_free_servernum() {\n"
                  "  i=$SERVERNUM\n"
                  "  while [ -f /tmp/.X$i-lock ]; do\n"
                  "    i=$(($i + 1))\n"
                  "  done\n"
                  "  echo $i\n"
                  "}\n"
                  "\n"
                  "tries=10\n"
                  "while [ $tries -gt 0 ]; do\n"
                  "  tries=$(( $tries - 1 ))\n"
                  "  Xvfb \":$SERVERNUM\" -auth /dev/null >&2 &\n"
                  "  XVFBPID=$!\n"
                  "  sleep 3 # wait before starting commands\n"
                  "\n"
                  "  if kill -0 $XVFBPID 2>/dev/null; then\n"
                  "    break\n"
                  "  else # server is in use, try another one\n"
                  "    SERVERNUM=$((SERVERNUM + 1))\n"
                  "    SERVERNUM=$(find_free_servernum)\n"
                  "    continue\n"
                  "  fi\n"
                  "  error \"Xvfb failed to start\" >&2\n"
                  "done\n"
                  "\n"
                  "export DISPLAY=:$SERVERNUM\n")
        if settings.PYTHON_VIRTENV != "":
            fsh.write("source " + os.path.join( settings.PYTHON_VIRTENV, "bin", "activate") + "\n")
        fsh.write(scommand + "\n")
        fsh.write("RETURN_CODE=$?\n")
        if settings.PYTHON_VIRTENV != "":
            fsh.write("deactivate\n")
        fsh.write("kill $XVFBPID\n")
        fsh.write("exit $RETURN_CODE\n")
        
    return filename


def generate_sge_script(scommand, fout):
    with open(fout+".sge.sh", "w") as fsh:
        fsh.write("#!/bin/bash\n")
        fsh.write("#$ -S /bin/bash\n")
        fsh.write("#$ -o "+fout + "\n")
        fsh.write("#$ -e "+fout+".err\n")
        fsh.write("#$ -v DISPLAY\n\n")
        fsh.write(scommand + "\n")
    return fout+".sge.sh"


def job_submission(fscript):
    qsub_command = ['qsub']
    qsub_command.extend( settings.QSUB_FLAGS)
    qsub_command.append(fscript)
    
    try:
        p1 = Popen(qsub_command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    except OSError as e:
        logger.error('error in qsub ' + str(e) + '\ncommand:\n' + (' '.join(qsub_command)) + '\nstderr:\n' + p1.communicate()[1])
        return False
    # try for 5 seconds if job is done
    i = 0
    while p1.poll() is None:
        ++i
        if( i >=5):
            p1.kill()
            logger.error('qsub does not finish within 5 seconds')
            return False
        sleep( 1)
    #success
    if( p1.returncode == 0):
        return True
    
    logger.error('qsub was not successful\ncommand:\n' + (' '.join(qsub_command)) + '\nreturncode:\n' + str(p1.returncode)+ "\nstderr:\n" + p1.communicate()[1])
    return False

