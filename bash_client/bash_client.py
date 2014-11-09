from subprocess import Popen, PIPE
import time
import copy
import threading
import signal
import os


def execute_command(command,
                    environment=None,
                    retry_return_codes=None,
                    number_of_retries=0,
                    command_sleep=0,
                    command_timeout=0):
    """
    :param command: Command and it's parameters in a List as Strings
    :param retry_return_codes: List of return codes that we should retry command on
    :param number_of_retries: Integer number of amount of retries to do
    :param command_sleep: Integer number of seconds to sleep for after executing command
    :param command_timeout: Integer number of seconds to wait before killing the command process
    :return: results as tuple stdout, sterr, returncode
    """
    if not retry_return_codes:
        retry_return_codes = []

    def run():
        if command_timeout:
            kill_check = threading.Event()

            def _kill_process_after_a_timeout(pid):
                os.kill(pid, signal.SIGTERM)
                kill_check.set()  # tell the main routine that we had to kill
                # use SIGKILL if hard to kill...
                return
            proc = Popen(command, stdout=PIPE, stderr=PIPE, env=environment)
            pid = proc.pid
            watchdog = threading.Timer(command_timeout, _kill_process_after_a_timeout, args=(pid, ))
            watchdog.start()
            stdout, stderr = proc.communicate()
            watchdog.cancel()  # if it's still waiting to run
            returncode = proc.returncode
            if kill_check.isSet():
                returncode = -404
                stdout = u"The process took to long to execute and timed out. " \
                         u"The timeout time is {0} seconds".format(command_timeout)
        else:
            proc = Popen(command, stdout=PIPE, stderr=PIPE, env=environment)
            stdout, stderr = proc.communicate()
            returncode = proc.returncode
        return stdout, stderr, returncode

    number_of_retries += 1  # number of retires plus the initial run
    retry_return_codes.append(-404)  # this return code is when the process has timed out
    stdout = None
    stderr = None
    returncode = None
    for retry in range(number_of_retries):
        stdout, stderr, returncode = run()
        time.sleep(command_sleep)
        if returncode not in retry_return_codes:
            break
    return stdout, stderr, returncode


def log_execute_command_results(command,
                                datetime_executed,
                                action,
                                returncode,
                                stdout,
                                stderr,
                                log_directory,
                                log_file_name='',
                                server='',
                                username=''):
    """
    :param command: Command executed as string
    :param datetime_executed: Datetime command was executed as Datetime object
    :param username: Name of user who executed command as string
    :param action: Name of action this command does as string
    :param returncode: Return code from subprocess
    :param stdout: Standard out from subprocess
    :param stderr: Standard error from subprocess
    :param server: Hostname or IP Address of server as string
    :param log_directory: UNIX directory path where to store log file
    :param log_file_name: Name of log file
    :return: None

    Writes a log of the executed command to the specified location and file
    """
    copied_cmd = copy.deepcopy(command)

    if not log_directory:
        raise ValueError('No log directory specified.')

    log_directory = log_directory.rstrip('/')

    if not log_file_name:
        log_file_name = 'execution_logs.txt'

    log_file_name = log_file_name.lstrip('/')

    with open(log_directory + '/' + log_file_name, "a") as myLog:
        myLog.write("===============================================================\n")
        myLog.write("---------------------------------------------------------------\n")
        myLog.write("DATETIME:\t\t{0}\n".format(datetime_executed))
        myLog.write("USERNAME:\t\t{0}\n".format(username))
        myLog.write("ACTION:\t\t\t{0}\n".format(action))
        myLog.write("SERVER:\t{0}\n".format(server))
        myLog.write("COMMAND:\t\t{0}\n".format(copied_cmd))
        myLog.write("RETURN CODE:\t{0}\n".format(returncode))
        myLog.write("STANDARD OUT:\n")
        myLog.write("{0}".format(stdout))
        myLog.write("STANDARD ERROR:\n")
        myLog.write("{0}".format(stderr))
        myLog.write("---------------------------------------------------------------\n")
        myLog.write("===============================================================\n")
        myLog.write("\n")
        myLog.close()
    return