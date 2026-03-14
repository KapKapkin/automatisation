FROM jetbrains/teamcity-agent:2025.11.3

USER root

RUN apt-get update -qq && \
    apt-get install -y -qq python3-pip postgresql-client > /dev/null 2>&1 && \
    pip3 install --break-system-packages --timeout=300 flake8==7.0.0 bandit==1.9.4 sqlfluff==3.3.1 && \
    pip3 install --break-system-packages --timeout=300 Django==5.0.2 psycopg2-binary==2.9.9 python-dotenv==1.0.1 gunicorn==21.2.0 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
