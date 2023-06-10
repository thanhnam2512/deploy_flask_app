import paramiko

# SSH connection details
hostname = '192.168.1.17'
username = 'deploy'
password = 'abcde@1234'

# Source and destination file paths
source_files = ['hello.py', 'requirements.txt', 'Dockerfile']
destination_path = '/home/deploy/flask_app/'

# Docker build command
docker_build_command = 'docker build -t myflaskapp .'

# Run Docker image
run_command = 'docker run -d -p 5000:5000 --name flask_app_container myflaskapp'

# SSH connection setup
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname, username=username, password=password)

# SFTP file transfer
sftp_client = ssh_client.open_sftp()
for file in source_files:
    source_path = './source/' + file  # Assuming the script is in the same directory as the files
    destination_path_file = destination_path + file
    sftp_client.put(source_path, destination_path_file)
    print(f'File "{file}" copied to "{destination_path}"')

# Check if the container is already running
check_command = 'docker ps -a --filter name=flask_app_container --format "{{.Names}}"'
stdin, stdout, stderr = ssh_client.exec_command(check_command)
container_name = stdout.read().decode('utf-8').strip()

# Stop and remove the container if it exists
if container_name == 'flask_app_container':
    stop_command = 'docker stop flask_app_container'
    remove_command = 'docker rm -f flask_app_container'
    ssh_client.exec_command(stop_command)
    ssh_client.exec_command(remove_command)
    print("Existing container stopped and removed.")

# Execute Docker build and Docker run command
stdin, stdout, stderr = ssh_client.exec_command(f'cd {destination_path} && {docker_build_command} && {run_command}')
build_output = stdout.read().decode('utf-8')
error_output = stderr.read().decode('utf-8')

# Print the build output
print(build_output)

# Print the error if any
if error_output:
    print("Error:")
    print(error_output)

# # Execute the Docker run command
# stdin, stdout, stderr = ssh_client.exec_command(f'cd {destination_path} && {run_command}')
# build_output = stdout.read().decode('utf-8')

# # Print the build output
# print(build_output)


# Close the SSH and SFTP connections
try: 
    sftp_client.close()
    ssh_client.close()
except AttributeError:
    pass
