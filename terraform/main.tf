terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  required_version = ">= 0.14.9"
}

provider "aws" {
  alias   = "Irlanda"
  profile = "default"
  region  = "eu-west-1"
}

provider "aws" {
  alias   = "Oregon"
  profile = "default"
  region  = "us-west-2"
}

provider "aws" {
  alias   = "Seul"
  profile = "default"
  region  = "ap-northeast-2"
}

provider "aws" {
  alias   = "Sydney"
  profile = "default"
  region  = "ap-southeast-2"
}



resource "aws_instance" "node01" {
  provider      = aws.Irlanda
  ami           = "ami-0b850cf02cc00fdc8"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.main-subnet-irlanda.id
  key_name      = "irlanda"
  tags = {
    Name = "node01.racpfg.com"
  }
}

resource "aws_instance" "node05" {
  provider      = aws.Irlanda
  ami           = "ami-0b850cf02cc00fdc8"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.main-subnet-irlanda.id
  key_name      = "irlanda"
  tags = {
    Name = "node05.racpfg.com"
  }
}

resource "aws_instance" "jmeter" {
  provider      = aws.Irlanda
  ami           = "ami-0b850cf02cc00fdc8"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.main-subnet-irlanda.id
  key_name      = "irlanda"
  tags = {
    Name = "jmeter.racpfg.com"
  }
}

resource "aws_instance" "proxy" {
  provider      = aws.Irlanda
  ami           = "ami-0b850cf02cc00fdc8"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.main-subnet-irlanda.id
  key_name      = "irlanda"
  tags = {
    Name = "proxy.racpfg.com"
  }
}

resource "aws_instance" "master" {
  provider      = aws.Irlanda
  ami           = "ami-0b850cf02cc00fdc8"
  instance_type = "t3.large"
  subnet_id     = aws_subnet.main-subnet-irlanda.id
 key_name      = "irlanda"
  tags = {
    Name = "master.racpfg.com"
  }
}




resource "aws_instance" "node02" {
  provider      = aws.Oregon
  ami           = "ami-0bc06212a56393ee1"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.main-subnet-oregon.id
  key_name      = "oregon"


  tags = {
    Name = "node02.racpfg.com"
  }
}

resource "aws_instance" "node06" {
  provider      = aws.Oregon
  ami           = "ami-0bc06212a56393ee1"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.main-subnet-oregon.id
  key_name      = "oregon"


  tags = {
    Name = "node06.racpfg.com"
  }
}





resource "aws_instance" "node03" {
  provider      = aws.Seul
  ami           = "ami-06e83aceba2cb0907"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.main-subnet-seul.id
  key_name      = "seul"

  tags = {
    Name = "node03.racpfg.com"
  }
}

resource "aws_instance" "node07" {
  provider      = aws.Seul
  ami           = "ami-06e83aceba2cb0907"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.main-subnet-seul.id
  key_name      = "seul"

  tags = {
    Name = "node07.racpfg.com"
  }
}



resource "aws_instance" "node04" {
  provider      = aws.Sydney
  ami           = "ami-0b2045146eb00b617"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.main-subnet-sydney.id
  key_name      = "sidney"

  tags = {
    Name = "node04.racpfg.com"
  }
}




resource "aws_instance" "node08" {
  provider      = aws.Sydney
  ami           = "ami-0b2045146eb00b617"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.main-subnet-sydney.id
  key_name      = "sidney"

  tags = {
    Name = "node08.racpfg.com"
  }
}





















resource "aws_vpc" "main-irlanda" {
  provider   = aws.Irlanda
  cidr_block = "172.20.0.0/16"

  tags = {
    Name = "K8auto-ireland"
  }
}

resource "aws_subnet" "main-subnet-irlanda" {
  provider   = aws.Irlanda
  vpc_id     = aws_vpc.main-irlanda.id
  cidr_block = "172.20.1.0/24"
  tags = {
    Name = "k8auto-subnet-ireland"
  }
}

resource "aws_internet_gateway" "autogw-irlanda" {
  provider = aws.Irlanda
  vpc_id   = aws_vpc.main-irlanda.id

  tags = {
    Name = "AutoGatewayIrlanda"
  }
}

resource "aws_route_table" "route-irlanda" {
  provider = aws.Irlanda
  vpc_id   = aws_vpc.main-irlanda.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.autogw-irlanda.id
  }

  route {
    cidr_block                = "172.21.1.0/24"
    vpc_peering_connection_id = aws_vpc_peering_connection.irlanda-oregon.id
  }
  route {
    cidr_block                = "172.22.1.0/24"
    vpc_peering_connection_id = aws_vpc_peering_connection.irlanda-seul.id
  }
  route {
    cidr_block                = "172.23.1.0/24"
    vpc_peering_connection_id = aws_vpc_peering_connection.irlanda-sydney.id
  }

  tags = {
    Name = "route-auto-irlanda"
  }
}


resource "aws_route_table_association" "asocirlanda" {
   provider      = aws.Irlanda
  subnet_id      = aws_subnet.main-subnet-irlanda.id
  route_table_id = aws_route_table.route-irlanda.id
}


resource "aws_main_route_table_association" "vpcasocirlanda" {
  provider      = aws.Irlanda
  vpc_id         = aws_vpc.main-irlanda.id
  route_table_id = aws_route_table.route-irlanda.id
}





resource "aws_vpc_peering_connection" "irlanda-oregon" {
  provider    = aws.Irlanda
  vpc_id      = aws_vpc.main-irlanda.id
  peer_vpc_id = aws_vpc.main-oregon.id
  peer_region = "us-west-2"

  tags = {
    Name = "VPC Peering entre Irlanda y Oregon"
  }
}



resource "aws_vpc_peering_connection_accepter" "aceptar-irlanda-oregon" {
  provider                  = aws.Oregon
  vpc_peering_connection_id = aws_vpc_peering_connection.irlanda-oregon.id
  auto_accept               = true

  tags = {
    Side = "Aceptacion"
  }
}



resource "aws_vpc_peering_connection" "irlanda-seul" {
  provider    = aws.Irlanda
  vpc_id      = aws_vpc.main-irlanda.id
  peer_vpc_id = aws_vpc.main-seul.id
  peer_region = "ap-northeast-2"

  tags = {
    Name = "VPC Peering entre Irlanda y Seul"
  }
}

resource "aws_vpc_peering_connection_accepter" "aceptar-irlanda-seul" {
  provider                  = aws.Seul
  vpc_peering_connection_id = aws_vpc_peering_connection.irlanda-seul.id
  auto_accept               = true

  tags = {
    Side = "Aceptacion"
  }
}


resource "aws_vpc_peering_connection" "irlanda-sydney" {
  provider    = aws.Irlanda
  vpc_id      = aws_vpc.main-irlanda.id
  peer_vpc_id = aws_vpc.main-sydney.id
  peer_region = "ap-southeast-2"

  tags = {
    Name = "VPC Peering entre Irlanda y Sydney"
  }
}

resource "aws_vpc_peering_connection_accepter" "aceptar-irlanda-sydney" {
  provider                  = aws.Sydney
  vpc_peering_connection_id = aws_vpc_peering_connection.irlanda-sydney.id
  auto_accept               = true

  tags = {
    Side = "Aceptacion"
  }
}



















resource "aws_vpc" "main-oregon" {
  provider   = aws.Oregon
  cidr_block = "172.21.0.0/16"

  tags = {
    Name = "K8auto-oregon"
  }
}


resource "aws_subnet" "main-subnet-oregon" {
  provider   = aws.Oregon
  vpc_id     = aws_vpc.main-oregon.id
  cidr_block = "172.21.1.0/24"
  tags = {
    Name = "k8auto-subnet-oregon"
  }
}
resource "aws_internet_gateway" "autogw-oregon" {
  provider = aws.Oregon
  vpc_id   = aws_vpc.main-oregon.id

  tags = {
    Name = "AutoGatewayOregon"
  }
}

resource "aws_route_table" "route-oregon" {
  provider = aws.Oregon
  vpc_id   = aws_vpc.main-oregon.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.autogw-oregon.id
  }

  route {
    cidr_block                = "172.20.1.0/24"
    vpc_peering_connection_id = aws_vpc_peering_connection.irlanda-oregon.id
  }
  route {
    cidr_block                = "172.22.1.0/24"
    vpc_peering_connection_id = aws_vpc_peering_connection.oregon-seul.id
  }
  route {
    cidr_block                = "172.23.1.0/24"
    vpc_peering_connection_id = aws_vpc_peering_connection.oregon-sydney.id
  }




  tags = {
    Name = "route-auto-oregon"
  }
}



resource "aws_route_table_association" "asocoregon" {
  provider      = aws.Oregon
  subnet_id      = aws_subnet.main-subnet-oregon.id
  route_table_id = aws_route_table.route-oregon.id
}



resource "aws_main_route_table_association" "vpcasocoregon" {
  provider      = aws.Oregon
  vpc_id         = aws_vpc.main-oregon.id
  route_table_id = aws_route_table.route-oregon.id
}





resource "aws_vpc_peering_connection" "oregon-sydney" {
  provider    = aws.Oregon
  vpc_id      = aws_vpc.main-oregon.id
  peer_vpc_id = aws_vpc.main-sydney.id
  peer_region = "ap-southeast-2"



  tags = {
    Name = "VPC Peering entre Oregon y Sydney"
  }
}


resource "aws_vpc_peering_connection_accepter" "aceptar-oregon-sydney" {
  provider                  = aws.Sydney
  vpc_peering_connection_id = aws_vpc_peering_connection.oregon-sydney.id
  auto_accept               = true

  tags = {
    Side = "Aceptacion"
  }
}






resource "aws_vpc_peering_connection" "oregon-seul" {
  provider    = aws.Oregon
  vpc_id      = aws_vpc.main-oregon.id
  peer_vpc_id = aws_vpc.main-seul.id
  peer_region = "ap-northeast-2"

  tags = {
    Name = "VPC Peering entre Oregon y Seul"
  }
}


resource "aws_vpc_peering_connection_accepter" "aceptar-oregon-seul" {
  provider                  = aws.Seul
  vpc_peering_connection_id = aws_vpc_peering_connection.oregon-seul.id
  auto_accept               = true

  tags = {
    Side = "Aceptacion"
  }
}



















resource "aws_vpc" "main-seul" {
  provider   = aws.Seul
  cidr_block = "172.22.0.0/16"

  tags = {
    Name = "K8auto-seul"
  }
}

resource "aws_subnet" "main-subnet-seul" {
  provider   = aws.Seul
  vpc_id     = aws_vpc.main-seul.id
  cidr_block = "172.22.1.0/24"
  tags = {
    Name = "k8auto-subnet-seul"
  }
}

resource "aws_internet_gateway" "autogw-seul" {
  provider = aws.Seul
  vpc_id   = aws_vpc.main-seul.id

  tags = {
    Name = "AutoGatewaySeul"
  }
}

resource "aws_route_table" "route-seul" {
  provider = aws.Seul
  vpc_id   = aws_vpc.main-seul.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.autogw-seul.id
  }

  route {
    cidr_block                = "172.20.1.0/24"
    vpc_peering_connection_id = aws_vpc_peering_connection.irlanda-seul.id
  }
  route {
    cidr_block                = "172.21.1.0/24"
    vpc_peering_connection_id = aws_vpc_peering_connection.oregon-seul.id
  }
  route {
    cidr_block                = "172.23.1.0/24"
    vpc_peering_connection_id = aws_vpc_peering_connection.seul-sydney.id
  }




  tags = {
    Name = "route-auto-seul"
  }
}

resource "aws_route_table_association" "asocseul" {
   provider      = aws.Seul
  subnet_id      = aws_subnet.main-subnet-seul.id
  route_table_id = aws_route_table.route-seul.id
}

resource "aws_main_route_table_association" "vpcasocseul" {
  provider      = aws.Seul
  vpc_id         = aws_vpc.main-seul.id
  route_table_id = aws_route_table.route-seul.id
}





resource "aws_vpc_peering_connection" "seul-sydney" {
  provider    = aws.Seul
  vpc_id      = aws_vpc.main-seul.id
  peer_vpc_id = aws_vpc.main-sydney.id
  peer_region = "ap-southeast-2"



  tags = {
    Name = "VPC Peering entre Seul y Sydney"
  }
}



resource "aws_vpc_peering_connection_accepter" "aceptar-seul-sydney" {
  provider                  = aws.Sydney
  vpc_peering_connection_id = aws_vpc_peering_connection.seul-sydney.id
  auto_accept               = true

  tags = {
    Side = "Aceptacion"
  }
}









resource "aws_vpc" "main-sydney" {
  provider   = aws.Sydney
  cidr_block = "172.23.0.0/16"

  tags = {
    Name = "K8auto-sydney"
  }
}


resource "aws_subnet" "main-subnet-sydney" {
  provider   = aws.Sydney
  vpc_id     = aws_vpc.main-sydney.id
  cidr_block = "172.23.1.0/24"
  tags = {
    Name = "k8auto-subnet-sydney"
  }
}


resource "aws_internet_gateway" "autogw-sydney" {
  provider = aws.Sydney
  vpc_id   = aws_vpc.main-sydney.id

  tags = {
    Name = "AutoGatewaySydney"
  }
}

resource "aws_route_table" "route-sydney" {
  provider = aws.Sydney
  vpc_id   = aws_vpc.main-sydney.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.autogw-sydney.id
  }


  route {
    cidr_block                = "172.20.1.0/24"
    vpc_peering_connection_id = aws_vpc_peering_connection.irlanda-sydney.id
  }
  route {
    cidr_block                = "172.21.1.0/24"
    vpc_peering_connection_id = aws_vpc_peering_connection.oregon-sydney.id
  }
  route {
    cidr_block                = "172.22.1.0/24"
    vpc_peering_connection_id = aws_vpc_peering_connection.seul-sydney.id
  }






  tags = {
    Name = "route-auto-sydney"
  }
}


resource "aws_route_table_association" "asocsydney" {
   provider      = aws.Sydney
  subnet_id      = aws_subnet.main-subnet-sydney.id
  route_table_id = aws_route_table.route-sydney.id
}

resource "aws_main_route_table_association" "vpcasocsydney" {
  provider      = aws.Sydney
  vpc_id         = aws_vpc.main-sydney.id
  route_table_id = aws_route_table.route-sydney.id
}
