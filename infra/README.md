# DineOps Infrastructure Services

This directory contains isolated Docker configurations for MySQL, Redis, and phpMyAdmin services that can be run independently of the main application.

## Directory Structure

```
infra/
├── mysql/
│   └── docker-compose.yml
├── phpmyadmin/
│   └── docker-compose.yml
├── redis/
│   ├── docker-compose.yml
│   └── redis.conf
├── .env
├── start_infra.sh
└── stop_infra.sh
```

## Usage

### Running Individual Services

#### Running MySQL Service

1. Navigate to the MySQL directory:
   ```bash
   cd infra/mysql
   ```

2. Start the MySQL service:
   ```bash
   docker-compose up -d
   ```

#### Running Redis Service

1. Navigate to the Redis directory:
   ```bash
   cd infra/redis
   ```

2. Start the Redis service:
   ```bash
   docker-compose up -d
   ```

#### Running phpMyAdmin Service

1. Navigate to the phpMyAdmin directory:
   ```bash
   cd infra/phpmyadmin
   ```

2. Start the phpMyAdmin service:
   ```bash
   docker-compose up -d
   ```

### Running the Complete Infrastructure Stack

#### Using the Startup Script (Recommended)

From the infra directory, you can use the provided startup script:
```bash
./start_infra.sh
```

This script will:
1. Check if MySQL is running, start it if not
2. Check if Redis is running, start it if not
3. Check if phpMyAdmin is running, start it if not
4. Display connection information for all services

The script automatically handles port conflicts and service dependencies.

### Stopping the Complete Infrastructure Stack

#### Using the Stop Script (Recommended)

From the infra directory, you can use the provided stop script:
```bash
./stop_infra.sh
```

This script will:
1. Stop phpMyAdmin service
2. Stop Redis service
3. Stop MySQL service
4. Display confirmation message

## Environment Variables

All services use the shared `.env` file in the infra directory for configuration.

### Shared Environment Variables
- `MYSQL_ROOT_PASSWORD`: Root user password
- `MYSQL_DATABASE`: Default database name
- `MYSQL_USER`: Default user
- `MYSQL_PASSWORD`: Default user password
- `MYSQL_PORT`: Port to expose for MySQL (default: 3306)
- `REDIS_PORT`: Port to expose for Redis (default: 6379)
- `PMA_PORT`: Port to expose for phpMyAdmin (default: 8080)
- `PMA_HOST`: Host for phpMyAdmin to connect to MySQL (default: host.docker.internal)

## Data Persistence

Data is persisted in Docker volumes:
- `mysql_mysql_data`: MySQL data
- `redis_redis_data`: Redis data

## Health Checks

All services include health checks:
- MySQL: Uses `mysqladmin ping`
- Redis: Uses `redis-cli ping`
- phpMyAdmin: Depends on MySQL service

## Stopping Services

### Stopping Individual Services
```bash
# Stop MySQL
cd mysql && docker-compose down

# Stop Redis
cd redis && docker-compose down

# Stop phpMyAdmin
cd phpmyadmin && docker-compose down
```

### Stopping All Infrastructure Services
```bash
# Stop all infrastructure services
cd mysql && docker-compose down && cd -
cd redis && docker-compose down && cd -
cd phpmyadmin && docker-compose down && cd -
```