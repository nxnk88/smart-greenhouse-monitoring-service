# Terraform / OpenStack

Конфигурация создаёт инфраструктуру OpenStack для сервиса
`smart-greenhouse-monitoring-service`: приватную сеть, подсеть, роутер,
Security Group, SSH keypair, порт виртуальной машины, Floating IP и VM.
Cloud-init устанавливает Docker и запускает контейнер приложения.

## Подготовка

Создайте локальный `clouds.yaml` с профилем `myopenstack` в текущем каталоге
или в `~/.config/openstack/clouds.yaml`. Файл содержит секреты и исключён из Git.

```yaml
clouds:
  myopenstack:
    auth:
      auth_url: https://openstack.example.com:5000/v3
      username: YOUR_USERNAME
      password: YOUR_PASSWORD
      project_name: YOUR_PROJECT
      user_domain_name: Default
      project_domain_name: Default
    region_name: RegionOne
    interface: public
    identity_api_version: 3
```

Скопируйте пример переменных и укажите значения своего облака:

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
```

## Развёртывание

```powershell
.\terraform-init.ps1
terraform validate
terraform plan
terraform apply
terraform output
```

Terraform выводит `public_ip`, `service_url`, `health_url`,
`optimal_greenhouses_url` и `ssh_command`.

Проверка приложения:

```powershell
$ip = terraform output -raw public_ip
curl.exe http://${ip}:8000/health
curl.exe http://${ip}:8000/optimal-greenhouses
```

Удаление ресурсов:

```powershell
terraform destroy
```

