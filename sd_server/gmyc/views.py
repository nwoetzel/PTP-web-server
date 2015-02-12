from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django import forms
from ptp.models import Jobs
from subprocess import Popen
import os
import logging
from time import sleep
import subprocess

logger = logging.getLogger(__name__)

class GMYCForm(forms.Form):
    treefile = forms.FileField(label='My ultrametric input tree (Newick format only):')
    method = forms.ChoiceField(choices = (("s", "Single threshold"), ("m", "Multi threshold")), label = 'Method:')
    #pvalue = forms.DecimalField(label = 'P-value:', initial = 0.01)
    sender = forms.EmailField(label='My e-mail address:')


def index(request):
    context = {}
    return render(request, 'index.html', context)


def thanks(request):
    return HttpResponse("Thanks for using our service!")


def autherror(request):
    return HttpResponse("Job id does not exists or e-mail address does not match!")


def queue_error(request):
    return HttpResponse("There is something wrong with the computational queue, please try again later!")


def gmyc_index(request):
    if request.method == 'POST': # If the form has been submitted...
        gmyc_form = GMYCForm(request.POST, request.FILES) # A form bound to the POST data
        if gmyc_form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            job = Jobs()
            job.email = gmyc_form.cleaned_data['sender']
            job.data_type = "umtree"
            job.method = "GMYC"
            job.save()
            filepath = os.path.join( settings.JOB_FOLDER, str(job.id))
            os.mkdir(filepath)
            newfilename = os.path.join( filepath, "input.tre")
            handle_uploaded_file(fin = request.FILES['treefile'] , fout = newfilename)
            job.filepath = filepath
            job.save()
            #pvalue = gmyc_form.cleaned_data['pvalue']
            #os.chmod(filepath, 0777)
            
            mode = gmyc_form.cleaned_data['method']
            
            jobok = run_gmyc_queue(fin = newfilename, fout = filepath + "output", mode = mode)
            if jobok:
                return show_gmyc_result(request, job_id = str(job.id), email = job.email)
            else:
                return queue_error(request)
            
    else:
        gmyc_form = GMYCForm() # An unbound form
    context = {'pform':gmyc_form}
    return render(request, 'gmyc/index.html', context)


def show_gmyc_result(request, job_id = "", email = ""):
    if job_id == "" or email == "":
        job_id = request.GET.get('job_id', '')
        email = request.GET.get('email', '')
    
    jobs = Jobs.objects.filter(id=job_id)
    if len(jobs) > 0:
        if jobs[0].email != email:
            return autherror(request)
    else:
        return autherror(request)
    
    out_path = os.path.join( settings.JOB_FOLDER, job_id, "input.tre_summary")
    #screenout = settings.MEDIA_ROOT + job_id + "/output"
    err = os.path.join( settings.JOB_FOLDER, job_id, "output.err")
    plot = os.path.join( settings.JOB_FOLDER, job_id, "input.tre_plot.png")
    
    if os.path.exists(out_path) and os.path.exists(plot):
        with open(out_path) as outfile:
            lines = outfile.readlines()
            results="<br/>".join(lines)
            context = {'result':results, 'jobid':job_id}
            return render(request, 'gmyc/results.html', context)
    else:
        with open(err) as ferr:
            lines = ferr.readlines()
            if len(lines) > 5:
                return render(request, 'gmyc/results.html', {'result':"Something is wrong, please check your input file", 'jobid':job_id, 'email':email})
            else:
                return render(request, 'gmyc/results.html', {'result':"Job still running", 'jobid':job_id, 'email':email})


def handle_uploaded_file(fin, fout):
    with open(fout, 'w+') as destination:
        for chunk in fin.chunks():
            destination.write(chunk)


def generate_pbs_script(scommand, fout):
    filename = fout+".pbs.sh"
    with open(filename, "w") as fsh:
        fsh.write("#!/bin/bash\n")
        fsh.write("#PBS -S /bin/bash\n")
        fsh.write("#PBS -o "+ fout + "\n")
        fsh.write("#PBS -e "+ fout + ".err\n")
        fsh.write("#PBS -W umask=022\n\n") # readable by group and all also
        fsh.write(scommand + "\n")
    return filename


def run_gmyc_queue(fin, fout, mode = "s"):
    '''Run gmyc with the given input using the queueing system
    Keyword arguments:
    fin -- filename of input file
    fout -- filename of output file
    '''
    command = " ".join([settings.R_BINARY, settings.GMYC_R, fin, mode])
    pbs_script = generate_pbs_script(scommand = command, fout = fout)
    jobok = job_submission(fscript = pbs_script)

    return jobok


def run_gmyc(fin, fout, mode = "s"):
    #GMYC.py -t example/gmyc_example.tre -ps
    #Popen(["nohup", "python",  settings.MEDIA_ROOT + "bin" + "/GMYC.py", "-t", fin, "-pvalue", str(pv), "-ps"], stdout=open(fout, "w"), stderr=open(fout+".err", "w") )
    Popen(["nohup", settings.GMYC_R, fin, mode], stdout=open(fout, "w"), stderr=open(fout+".err", "w") )


def job_submission(fscript):
    qsub_command = ['qsub']
    qsub_command.extend(settings.QSUB_FLAGS)
    qsub_command.append(fscript)
    try:
        p1 = Popen(qsub_command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    except OSError as e:
        logger.error('error in qsub ' + str(e) + '\nstderr:\n' + p1.communicate()[1])
        return False
    # try for 5 seocnds if job is done
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
    
    logger.error('qsub was not successful:\nreturncode:\n' + str(p1.returncode) + "\nstderr:\n" + p1.communicate()[1])
    return False
