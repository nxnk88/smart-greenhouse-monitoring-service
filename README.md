# GreenPulse: мониторинг умных теплиц

Учебный DevOps-проект по дисциплине **«Технология проектирования
автоматизированных систем в защищённом исполнении»**.

**Тема:** разработка и развёртывание веб-сервиса мониторинга микроклимата
умных теплиц.

| Параметр | Значение |
| --- | --- |
| Проект | `smart-greenhouse-monitoring-service` |
| Выполнил | **Копань Артем Алексеевич** |
| Дата | 18.06.2026 |
| GitHub | `https://github.com/nxnk88/smart-greenhouse-monitoring-service` |

## 1. Цель работы

Разработать приложение с REST API и наглядной веб-панелью, упаковать его в
Docker, описать облачную инфраструктуру средствами Terraform и подготовить
развёртывание в OpenStack и Kubernetes/Minikube.

В проекте сохранён полный учебный цикл исходного варианта:

- FastAPI-приложение и интерактивная документация Swagger;
- обработка тестового набора данных через pandas;
- фильтрация, поиск объекта и вычисление объектов в оптимальном состоянии;
- Docker-образ и проверка состояния контейнера;
- OpenStack-инфраструктура через Terraform;
- автоматический запуск контейнера через cloud-init;
- Kubernetes Deployment на две реплики и NodePort Service.

## 2. Назначение приложения

`smart-greenhouse-monitoring-service` собирает показатели восьми учебных
теплиц: температуру, влажность воздуха, влажность почвы, уровень CO₂ и
состояние автоматического полива. Главная страница выполнена как адаптивный
dashboard GreenPulse, а те же данные доступны в JSON через REST API.

Параметры считаются оптимальными, когда одновременно выполняются условия:

- температура от `18` до `28 °C`;
- влажность воздуха от `55` до `80 %`;
- влажность почвы от `40` до `75 %`;
- уровень CO₂ не выше `1200 ppm`;
- автоматический полив включён.

## 3. Технологии

- Python 3.11, FastAPI, Uvicorn и pandas;
- HTML5, CSS3 и JavaScript без внешних frontend-зависимостей;
- Docker и Docker Hub;
- Terraform `>= 1.5.0` и OpenStack Provider `>= 3.0.0`;
- OpenStack, cloud-init, Kubernetes, Minikube и kubectl.

## 4. Структура репозитория

```text
.
├── app.py
├── static/
│   ├── index.html
│   ├── styles.css
│   └── dashboard.js
├── requirements.txt
├── Dockerfile
├── k8s/
│   ├── namespace.yaml
│   ├── deployment.yaml
│   └── service.yaml
├── terraform-openstack/
│   ├── versions.tf
│   ├── variables.tf
│   ├── main.tf
│   ├── outputs.tf
│   ├── cloud-init.yaml
│   ├── terraform.tfvars.example
│   ├── terraform-init.ps1
│   └── README.md
├── screenshots/
└── README.md
```

## 5. REST API

| Метод | Путь | Назначение |
| --- | --- | --- |
| `GET` | `/` | Панель мониторинга GreenPulse |
| `GET` | `/api` | Метаданные сервиса и автор работы |
| `GET` | `/health` | Проверка состояния приложения |
| `GET` | `/greenhouses` | Все теплицы |
| `GET` | `/greenhouses?zone=...` | Фильтр по сектору |
| `GET` | `/greenhouses?crop=...` | Фильтр по культуре |
| `GET` | `/greenhouse/{greenhouse_id}` | Поиск теплицы по идентификатору |
| `GET` | `/optimal-greenhouses` | Объекты с оптимальными параметрами |
| `GET` | `/summary` | Сводные показатели для dashboard |

Swagger UI доступен по адресу `http://127.0.0.1:8000/docs`, OpenAPI-схема —
по адресу `http://127.0.0.1:8000/openapi.json`.

## 6. Локальный запуск

```powershell
git clone https://github.com/nxnk88/smart-greenhouse-monitoring-service.git
Set-Location smart-greenhouse-monitoring-service
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Проверка:

```powershell
curl.exe http://127.0.0.1:8000/health
curl.exe http://127.0.0.1:8000/summary
curl.exe http://127.0.0.1:8000/optimal-greenhouses
curl.exe "http://127.0.0.1:8000/greenhouses?zone=Южный%20сектор"
```

## 7. Docker

Сборка и локальный запуск:

```powershell
docker build -t smart-greenhouse-monitoring-service:v1 .
docker rm -f greenhouse-monitor 2>$null
docker run -d --name greenhouse-monitor -p 8001:8000 smart-greenhouse-monitoring-service:v1
docker ps
curl.exe http://127.0.0.1:8001/health
curl.exe http://127.0.0.1:8001/optimal-greenhouses
```

В `Dockerfile` настроен встроенный `HEALTHCHECK`. Веб-интерфейс после запуска
доступен по адресу `http://127.0.0.1:8001/`.

Публикация образа:

```powershell
docker login
docker tag smart-greenhouse-monitoring-service:v1 xzxzxzxze/smart-greenhouse-monitoring-service:v1
docker push xzxzxzxze/smart-greenhouse-monitoring-service:v1
```

## 8. OpenStack и Terraform

Конфигурация в каталоге `terraform-openstack/` создаёт:

- приватную сеть `greenhouse-monitor-network` и подсеть;
- роутер с подключением к внешней сети;
- Security Group с правилами для `22/tcp` и `8000/tcp`;
- SSH keypair, сетевой порт, виртуальную машину и Floating IP;
- cloud-init сценарий установки Docker и запуска приложения.

Подготовка и запуск:

```powershell
Set-Location terraform-openstack
Copy-Item terraform.tfvars.example terraform.tfvars
.\terraform-init.ps1
terraform validate
terraform plan
terraform apply
terraform output
```

В `terraform.tfvars` необходимо указать реальные image, flavor, external
network и Docker image. Файлы `clouds.yaml`, `terraform.tfvars`, state и
локальные каталоги провайдера исключены из Git.

Проверка VM:

```powershell
$ip = terraform output -raw public_ip
curl.exe http://${ip}:8000/health
curl.exe http://${ip}:8000/optimal-greenhouses
ssh ubuntu@$ip
sudo docker ps
sudo docker logs greenhouse-monitor
```

Удаление ресурсов: `terraform destroy`.

## 9. Kubernetes / Minikube

Манифесты создают namespace `greenhouse-monitoring`, Deployment на две
реплики и NodePort Service на порту `30080`.

```powershell
minikube start --driver=docker
kubectl apply -f .\k8s\namespace.yaml
kubectl apply -f .\k8s\deployment.yaml
kubectl apply -f .\k8s\service.yaml
kubectl rollout status deployment/greenhouse-monitor-deployment -n greenhouse-monitoring
kubectl get pods,service,endpoints -n greenhouse-monitoring
```

Проверка через port-forward:

```powershell
kubectl port-forward -n greenhouse-monitoring service/greenhouse-monitor-service 18080:8000
curl.exe http://127.0.0.1:18080/health
curl.exe http://127.0.0.1:18080/summary
```

Остановка: `kubectl delete namespace greenhouse-monitoring` и
`minikube delete`.

## 10. Безопасность

В публичный репозиторий нельзя добавлять пароли, токены, приватные SSH-ключи,
`clouds.yaml`, реальные `terraform.tfvars`, файлы состояния Terraform и
локальный файл `server-credentials.local.md`. Все такие пути перечислены в
`.gitignore` и `.dockerignore`; в репозитории хранится только безопасный пример
`terraform.tfvars.example`.

Для реального стенда рекомендуется ограничить `ssh_cidr` и `app_cidr` вместо
значения `0.0.0.0/0`.

## 11. Иллюстрации

Каталог `screenshots/` подготовлен для снимков фактического развёртывания.
Старые скриншоты исходного варианта в новый репозиторий не переносятся,
поскольку они содержат другое название проекта и другие данные. После запуска
стенда сюда можно добавить dashboard, Swagger UI, Docker, OpenStack и
Kubernetes с актуальными именами ресурсов.

## 12. Результат

Создан самостоятельный вариант проекта — сервис мониторинга микроклимата
умных теплиц. Предметная область, данные, API, наименования облачных ресурсов и
визуальный стиль полностью изменены, при этом исходная учебная логика и все
этапы развёртывания сохранены.

