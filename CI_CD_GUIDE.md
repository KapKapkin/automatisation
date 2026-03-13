# Лабораторная работа: CI/CD с Docker и TeamCity

## Шаг 1. Загрузка образа приложения на DockerHub

```bash
# Авторизация в DockerHub
docker login

# Тегирование образа (замените YOUR_USERNAME на ваш DockerHub username)
docker tag automatisation-web:latest YOUR_USERNAME/automatisation-web:latest

# Загрузка на DockerHub
docker push YOUR_USERNAME/automatisation-web:latest
```

## Шаг 2. Развёртывание TeamCity

TeamCity уже сконфигурирован в `docker-compose.teamcity.yml`.

```bash
# Запуск TeamCity
docker compose -f docker-compose.teamcity.yml up -d

# Проверка статуса
docker compose -f docker-compose.teamcity.yml ps
```

## Шаг 3. Первоначальная настройка TeamCity

1. Откройте **http://localhost:8111** в браузере
2. Дождитесь загрузки (может занять 2-3 минуты при первом запуске)
3. На странице инициализации выберите **"Proceed"**
4. Выберите тип БД: **Internal (HSQLDB)** (для лабораторной достаточно)
5. Примите лицензионное соглашение
6. Создайте пользователя-администратора:
   - Username: `admin`
   - Password: (ваш пароль)

## Шаг 4. Создание пользователей для членов команды

1. Перейдите в **Administration** → **Users**
2. Нажмите **"Create user account"**
3. Заполните данные для каждого члена команды:
   - Username
   - Name
   - Password
4. Назначьте роли: **Project Developer** для проекта

## Шаг 5. Создание проекта и привязка репозитория

1. На главной странице нажмите **"Create project"**
2. Выберите **"From a repository URL"**
3. Укажите URL вашего Git-репозитория:
   - Для GitHub: `https://github.com/YOUR_USERNAME/automatisation.git`
   - Для SSH: `git@github.com:YOUR_USERNAME/automatisation.git`
4. При необходимости укажите учётные данные (username/token для GitHub)
5. Нажмите **"Proceed"**
6. Задайте имя проекта: `Automatisation - Аудиторный фонд`

## Шаг 6. Создание конфигурации сборки

### Конфигурация 1: Build & Push Docker Image

1. В проекте нажмите **"Create build configuration"**
2. Тип: **Manually**
3. Название: `Build and Push Docker Image`

#### 6.1 Настройка VCS Root (репозиторий)

1. Перейдите в **Build Configuration Settings** → **Version Control Settings**
2. Нажмите **"Attach VCS root"**
3. Выберите ранее созданный VCS root
4. **Branch specification**: `+:refs/heads/*` (для отслеживания всех веток)
5. **Default branch**: `refs/heads/main`

#### 6.2 Настройка Build Steps (шаги сборки)

**Шаг 1: Build Docker Image (для всех веток)**

1. Нажмите **"Add build step"**
2. Runner type: **Command Line**
3. Step name: `Build Docker Image`
4. Custom script:

```bash
BRANCH_NAME="%teamcity.build.branch%"
IMAGE_NAME="%env.DOCKER_USERNAME%/automatisation-web"

# Determine tag
if [[ "$BRANCH_NAME" == "main" || "$BRANCH_NAME" == "prod" ]]; then
    TAG="prod"
elif [[ "$BRANCH_NAME" == "dev" ]]; then
    TAG="dev"
else
    TAG=$(echo "$BRANCH_NAME" | sed 's|/|-|g')
fi

echo "Building image: ${IMAGE_NAME}:${TAG}"
docker build -t "${IMAGE_NAME}:${TAG}" .
```

**Шаг 2: Push to DockerHub (только для dev и prod/main)**

1. Нажмите **"Add build step"**
2. Runner type: **Command Line**
3. Step name: `Push to DockerHub`
4. Execute step: **If all previous steps finished successfully**
5. Custom script:

```bash
BRANCH_NAME="%teamcity.build.branch%"
IMAGE_NAME="%env.DOCKER_USERNAME%/automatisation-web"

if [[ "$BRANCH_NAME" == "main" || "$BRANCH_NAME" == "prod" ]]; then
    TAG="prod"
elif [[ "$BRANCH_NAME" == "dev" ]]; then
    TAG="dev"
else
    echo "Branch ${BRANCH_NAME} — skip push"
    exit 0
fi

echo "%env.DOCKER_PASSWORD%" | docker login -u "%env.DOCKER_USERNAME%" --password-stdin
docker push "${IMAGE_NAME}:${TAG}"

if [[ "$TAG" == "prod" ]]; then
    docker tag "${IMAGE_NAME}:${TAG}" "${IMAGE_NAME}:latest"
    docker push "${IMAGE_NAME}:latest"
fi
```

#### 6.3 Настройка Build Parameters

Перейдите в **Build Configuration Settings** → **Parameters**:

| Имя | Тип | Значение |
|-----|-----|----------|
| `env.DOCKER_USERNAME` | Environment variable | ваш DockerHub username |
| `env.DOCKER_PASSWORD` | Environment variable (type: Password) | ваш DockerHub пароль/токен |

#### 6.4 Настройка Triggers (триггеры)

1. Перейдите в **Build Configuration Settings** → **Triggers**
2. Нажмите **"Add new trigger"**
3. Выберите **"VCS Trigger"**
4. Branch filter:
   ```
   +:<default>
   +:dev
   +:prod
   ```

#### 6.5 Авторизация агента

1. Перейдите в **Administration** → **Agents**
2. Найдите незарегистрированного агента на вкладке **"Unauthorized"**
3. Нажмите **"Authorize"**

---

## Альтернативный вариант: использование скрипта ci/build-and-push.sh

Если предпочитаете один шаг сборки, можно создать единственный Build Step:

1. Runner type: **Command Line**
2. Step name: `Build and Push`
3. Custom script:
```bash
export BRANCH_NAME="%teamcity.build.branch%"
export DOCKER_USERNAME="%env.DOCKER_USERNAME%"
export DOCKER_PASSWORD="%env.DOCKER_PASSWORD%"
export BUILD_VCS_NUMBER="%build.vcs.number%"

chmod +x ci/build-and-push.sh
./ci/build-and-push.sh
```

---

## Проверка работы

1. Сделайте коммит в ветку `dev` → должна запуститься сборка, образ загрузится как `YOUR_USERNAME/automatisation-web:dev`

2. Сделайте коммит в ветку `main`/`prod` → образ загрузится как `YOUR_USERNAME/automatisation-web:prod` и `YOUR_USERNAME/automatisation-web:latest`

3. Коммит в любую другую ветку → образ собирается, но НЕ загружается на DockerHub

## Схема веток

```
main/prod  ──→  Build ──→ Push (tag: prod, latest)
dev        ──→  Build ──→ Push (tag: dev)
feature/*  ──→  Build only (no push)
```
