
#!/usr/bin/env python
import subprocess as sub
import shlex, sys, argparse, time, os
from multiprocessing import Process

def readCommandList(fIN):
    out = []
    for line in open(fIN).readlines():
        i = line.rstrip()
        out.append(shlex.split(i))
    return out

def submitJob(command):
    pid = os.getpid()
    logname = f'.job-{pid}.log'
    errname = f'.job-{pid}.err'
    print(f'running:> {" ".join(command)}')
    try:
        with open(logname, 'w') as log, open(errname, 'w') as err:
            x = sub.Popen(command, stdout=log, stderr=err)
            x.wait()
        os.remove(logname)
        os.remove(errname)
        return 0
    except Exception as e:
        print(f'Job Failed:> {" ".join(command)}')
        print(f'Error: {e}')
        return 1

def parseArgs():
    arg = argparse.ArgumentParser()
    arg.add_argument('commandList', type=str, help='list of commands in .sh format, each line will be a job')
    arg.add_argument('-n', type=int, default=2, help='number of processors to use, defaults to 2')
    arg.add_argument('--time', action='store_true', help='times how long the job takes to complete')
    return arg.parse_args()

def progress(num, outof):
    num = float(num)
    outof = float(outof)
    width = 30
    line = '['
    meter = '=' * int(num / outof * width) + ' ' * int((outof - num) / outof * width)
    line += meter[:width - 4]
    line += ']'
    line += f' {int(num)} / {int(outof)}'
    if num == 1:
        sys.stdout.write(line)
    elif num == outof:
        sys.stdout.write('\r' + line)
        sys.stdout.flush()
        sys.stdout.write("\n")
    else:
        sys.stdout.write('\r' + line)
        sys.stdout.flush()

def updateJobs(currentJobs, jobTrack):
    for i in range(len(currentJobs)):
        try:
            jobTrack[i] = currentJobs[i].is_alive()
        except:
            jobTrack[i] = 0
    return jobTrack

def batchSubmit(jobCommands, nproc=4):
    jobs = len(jobCommands)
    jobTrack = [0] * 24
    global currJobs
    currJobs = [None] * 24
    maxJobs = nproc

    while jobs:
        jobTrack = updateJobs(currJobs, jobTrack)
        runningJobs = sum(jobTrack)
        jobs = len(jobCommands)

        if not jobs:
            while runningJobs:
                time.sleep(1)
                jobTrack = updateJobs(currJobs, jobTrack)
                runningJobs = sum(jobTrack)
            break

        if runningJobs < maxJobs:
            a = jobCommands.pop()

            for i in range(len(jobTrack)):
                if jobTrack[i] == 0:
                    currJobs[i] = Process(target=submitJob, args=(a,))
                    print(f'running:> {" ".join(a)}')
                    currJobs[i].start()
                    break
        else:
            time.sleep(1)

if __name__ == '__main__':
    start = time.time()
    args = parseArgs()
    x = readCommandList(args.commandList)
    batchSubmit(x, args.n)
    if args.time:
        print(f'Total Runtime: {time.time() - start:.4f} seconds')
    sys.exit()
