from bash_client import bash_client

def remote_copy_files(files, destination_directory):
    """
    :param files: tuple or list of files with there directory paths to be copied over to the destination server (String)
    :param destination_directory: the directory the files will be copied to on the destination server (String)
    :return: Tuple of command execution status (Bool), Result Message (String)
    """
    if not isinstance(destination_directory, (str, basestring, unicode)):
	raise TypeError('destination_directory input variable is not a string or unicode type.')

    for index, file_name in enumerate(files):
	if not os.path.isfile(file_name):
	    raise IOError('files input variable at index {0} value {1} does not point to a valid file. '
			  'The location or filename maybe incorrect.'.format(index, file_name))

    # Set variables
    username = 'johndoe'
    private_key_file = '/root/automation_user.priv'
    hostname = 'linuxhost01.acme.com'
    command_timeout = 10
    command_sleep = 3
    

    command = ['scp',
		'-o',
		'UserKnownHostsFile=/dev/null',
		'-o',
		'StrictHostKeyChecking=no',
		'-i',
		'{SSH_KEY}'.format(SSH_KEY=private_key_file),
		'{USERNAME}@{HOSTNAME}:{DESTINATION}'.format(USERNAME=username,
							    HOSTNAME=hostname,
							    DESTINATION=destination_directory)]

    # Insert files into command after ssh_key
    for file in files:
	command.insert(7, file)

    stdout, stderr, returncode = bash_client.execute_command(command=command,
							      command_timeout=command_timeout,
							      command_sleep=command_sleep)

    bash_client.log_execute_command_results(command=command,
					    datetime_executed=datetime.now(),
					    action='SCP Files to remote server',
					    returncode=returncode,
					    stdout=stdout,
					    stderr=stderr,
					    log_directory='/tmp/',
					    server=hostname)

    if returncode == 0:
	command_execution_status = True
	result_message = u"Successfully scp files to {HOSTNAME}.".format(HOSTNAME=hostname)
    else:
	command_execution_status = False
	result_message = u"Failed to scp files to {HOSTNAME}.".format(HOSTNAME=hostname)
    return command_execution_status, result_message 
