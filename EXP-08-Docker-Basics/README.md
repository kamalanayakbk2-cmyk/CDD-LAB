

\# CDD Lab Experiment 8

\## Docker Installation and Basic Docker Commands



\### Aim

To install Docker, verify its installation, download Docker images, create and manage containers, and execute basic Docker commands.



\### Software Requirements

\- Windows 10/11

\- Docker Desktop

\- PowerShell



\### Commands Executed



1\. Check Docker version:

&#x20;  ```powershell

&#x20;  docker --version

&#x20;  ```



2\. Display Docker system information:

&#x20;  ```powershell

&#x20;  docker info

&#x20;  ```



3\. Test Docker installation:

&#x20;  ```powershell

&#x20;  docker run hello-world

&#x20;  ```



4\. Download Nginx image:

&#x20;  ```powershell

&#x20;  docker pull nginx

&#x20;  ```



5\. List downloaded images:

&#x20;  ```powershell

&#x20;  docker images

&#x20;  ```



6\. Create and run Nginx container:

&#x20;  ```powershell

&#x20;  docker run -d -p 8080:80 --name my-nginx nginx

&#x20;  ```



7\. List running containers:

&#x20;  ```powershell

&#x20;  docker ps

&#x20;  ```



8\. List all containers:

&#x20;  ```powershell

&#x20;  docker ps -a

&#x20;  ```



9\. Stop the Nginx container:

&#x20;  ```powershell

&#x20;  docker stop my-nginx

&#x20;  ```



10\. Remove the container:

&#x20;   ```powershell

&#x20;   docker rm my-nginx

&#x20;   ```



11\. Remove the Nginx image:

&#x20;   ```powershell

&#x20;   docker rmi nginx

&#x20;   ```



\### Result

Docker was successfully installed and tested. The Nginx image was downloaded, a container was created and executed, and container and image management commands were performed successfully.



