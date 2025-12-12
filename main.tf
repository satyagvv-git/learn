terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "6.24.0"
    }
  }
}

provider "aws" {
  # Configuration options
  region ="us-east-1"
 
}
resource "aws_instance" "example" {
  ami           = "ami-068c0051b15cdb816"
  instance_type = "t2.micro"

  tags = {
    Name = "HelloWorld"
  }
}

resource "aws_vpc" "myvpc"{
cidr_block = "10.10.0.0/16"

}