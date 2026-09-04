```text
1. Project structure
python-ec2-cicd/
│
├── app.py
├── requirements.txt
├── tests/
│   └── test_app.py
│
└── .github/
    └── workflows/
        └── deploy.yml
```

```text
The flow will be:

GitHub Repository
       |
       | Push to main
       v
GitHub Actions
       |
       +---- Build
       +---- Test
       +---- Package
       |
       | upload artifact
       v
GitHub Artifact Storage
       |
       | download artifact
       v
Deploy Job
       |
       | SCP / SSH
       v
EC2
       |
       v
/opt/python-app
       |
       v
Python virtual environment
```
```text
 EC2 preparation

Before running the pipeline, prepare your EC2 instance.

I'm assuming an Amazon Linux EC2 instance.

SSH into EC2:

ssh -i your-key.pem ec2-user@<EC2-IP>

Install Python:

sudo dnf install python3 python3-pip -y

Check:

python3 --version
7. Create application directory

On EC2:

sudo mkdir -p /opt/python-app

Give ownership to ec2-user:

sudo chown -R ec2-user:ec2-user /opt/python-app
8. Create systemd service

Create:

sudo vi /etc/systemd/system/python-app.service

Put:

[Unit]
Description=Python Flask Application
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/opt/python-app
ExecStart=/opt/python-app/venv/bin/python /opt/python-app/app.py
Restart=always

[Install]
WantedBy=multi-user.target

Then:

sudo systemctl daemon-reload

Enable it:

sudo systemctl enable python-app
The GitHub Actions deployment will restart it:
sudo systemctl restart python-app
```
```text
 GitHub Secrets

Go to:  GitHub → Repository → Settings → Secrets and variables → Actions
Create these three repository secrets: EC2_HOST  , EC2_USER  ,EC2_SSH_KEY


For a real production setup, I'd instead put NGINX/ALB in front of the application and avoid exposing 8080 publicly.

For this learning exercise, exposing 8080 is fine.

11. Push the project

Your final repository should look like:

python-ec2-cicd/
│
├── app.py
│
├── requirements.txt
│
├── tests/
│   └── test_app.py
│
└── .github/
    └── workflows/
        └── deploy.yml

```text
 What happens during the pipeline?
Job 1 — Build
checkout
   ↓
Install Python
   ↓
Install dependencies
   ↓
Run pytest
   ↓
Create python-app.tar.gz
   ↓
Upload artifact
Job 2 — Deploy

Because of:

needs: build

the deploy job waits for the build job.

Then:

Download artifact
       ↓
Configure SSH
       ↓
SCP package → EC2
       ↓
Extract package
       ↓
Create virtual environment
       ↓
pip install requirements
       ↓
systemctl restart python-app
```

```text
 Verify on EC2

After successful deployment:

sudo systemctl status python-app

You should see:

Active: active (running)

Check the application locally on EC2:

curl http://localhost:8080

Expected:

Hello from Python App deployed using GitHub Actions!

Health check:

curl http://localhost:8080/health

Expected:  OK

And from your browser:

http://<EC2-PUBLIC-IP>:8080
The key CI/CD concept we're demonstrating

This setup deliberately has two GitHub Actions jobs so you can see the artifact concept we discussed:

             GitHub Actions
                   |
          +--------+--------+
          |                 |
       BUILD              DEPLOY
          |                 ^
          |                 |
          +-- ARTIFACT -----+
                            |
                            v
                           EC2

There is no Docker, ECR, or ACR here.

The deployable artifact is:  python-app.tar.gz

GitHub Actions temporarily stores that artifact between the two jobs, and the Deploy job downloads it and transfers it to EC2 via SSH/SCP
```
