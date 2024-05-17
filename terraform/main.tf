provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "mpi_instances" {
  count         = 3  # Number of instances to launch
  ami           = "ami-04b70fa74e45c3917" 
  instance_type = "t2.micro"

  key_name = var.key_name

  security_groups = [aws_security_group.mpi_sg.name]

  tags = {
    Name = "mpi-instance-${count.index}"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y python3 python3-pip python3-opencv libopencv-dev mpich",
      "pip3 install mpi4py"
    ]

    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file(var.private_key_path)
      host        = self.public_ip
    }
  }
}

resource "aws_security_group" "mpi_sg" {
  name        = "mpi-sg"
  description = "Allow SSH and MPI traffic"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

variable "key_name" {
  description = "The name of the key pair to use for SSH access"
  type        = string
}

variable "private_key_path" {
  description = "The path to the private key for SSH access"
  type        = string
}
