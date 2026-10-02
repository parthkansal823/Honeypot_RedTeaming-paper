@echo off
REM ==============================================================================
REM Honeypot Research Paper - Windows Docker Management Script
REM ==============================================================================

if "%1"=="" goto help
if "%1"=="start-honeypot" goto start_honeypot
if "%1"=="stop-honeypot" goto stop_honeypot
if "%1"=="tables" goto generate_tables
if "%1"=="eval" goto run_eval
if "%1"=="attack" goto run_attack
goto help

:start_honeypot
echo Starting Cowrie Honeypot in Docker...
docker compose up -d cowrie
echo Cowrie is running on localhost:2222. Check logs with: docker compose logs -f cowrie
goto end

:stop_honeypot
echo Stopping Cowrie Honeypot...
docker compose stop cowrie
goto end

:generate_tables
echo Analyzing 120 existing sessions and generating paper tables...
docker compose run --rm attacker python generate_paper_tables.py
goto end

:run_eval
echo Running ML Transfer Classifier across Synthetic and Real datasets...
docker compose run --rm attacker python train_eval_classifier.py --synthetic normalized/live_synthetic.jsonl --real normalized/live_organic.jsonl
goto end

:run_attack
echo Running AI Attacker session inside Docker...
docker compose run --rm attacker python better_ai_attacker.py --host cowrie --port 2222 --username root --password root --sessions 5 --output logs/docker_run
goto end

:help
echo ==============================================================================
echo Honeypot Research Paper Docker Commands:
echo ==============================================================================
echo   run_docker.bat start-honeypot   - Launch Cowrie honeypot container on port 2222
echo   run_docker.bat stop-honeypot    - Stop Cowrie honeypot
echo   run_docker.bat tables           - Generate Table 1 and Table 2 from existing 120 logs
echo   run_docker.bat attack           - Launch AI attacker session against honeypot
echo   run_docker.bat eval             - Run the 4-quadrant ML defense transfer benchmark
echo ==============================================================================

:end
