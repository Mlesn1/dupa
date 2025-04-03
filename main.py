"""
Main entry point for the Discord Bot with PLLuM AI integration.
"""
import logging
import os
import sys
import time
import subprocess
import json
from datetime import datetime

# For Flask web interface
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Variables to track bot status
bot_status = {
    "is_running": False,
    "last_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "error": None
}

# Get configuration details
def get_config_details():
    """Get configuration details from environment files"""
    config = {
        "model": os.environ.get("PLLUM_MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.2"),
        "prefix": os.environ.get("COMMAND_PREFIX", "!"),
        "max_tokens": os.environ.get("PLLUM_MAX_TOKENS", "1024"),
        "temperature": os.environ.get("PLLUM_TEMPERATURE", "0.7"),
        "history_length": os.environ.get("MAX_HISTORY_LENGTH", "10"),
        "timeout": os.environ.get("CONVERSATION_TIMEOUT", "600"),
    }
    return config

@app.route('/api/bot-status', methods=['GET', 'POST'])
def bot_status_api():
    """API endpoint to get or update bot status"""
    global bot_status
    
    if request.method == 'POST':
        data = request.json
        if data and isinstance(data, dict):
            # Update bot status
            if 'is_running' in data:
                bot_status['is_running'] = data['is_running']
            if 'error' in data:
                bot_status['error'] = data['error']
            bot_status['last_check'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return jsonify({"status": "updated", "bot_status": bot_status})
        return jsonify({"status": "error", "message": "Invalid data format"}), 400
    
    # GET request - return current status
    return jsonify(bot_status)

@app.route('/api/start-bot', methods=['POST'])
def start_bot_api():
    """API endpoint to start the Discord bot"""
    try:
        # Check if bot is already running
        if bot_status['is_running']:
            return jsonify({
                "status": "warning", 
                "message": "Bot is already running"
            })
        
        # Start the bot in a subprocess
        process = subprocess.Popen(
            ["python", "run_discord_bot.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Update status to starting
        bot_status['is_running'] = True
        bot_status['error'] = None
        bot_status['last_check'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bot_status['start_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return jsonify({
            "status": "success", 
            "message": "Bot start initiated"
        })
    
    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
        return jsonify({
            "status": "error", 
            "message": f"Error starting bot: {str(e)}"
        }), 500

@app.route('/api/check-secrets', methods=['GET'])
def check_secrets_api():
    """API endpoint to check if required secrets are available"""
    required_secrets = ["DISCORD_TOKEN", "HUGGINGFACE_API_KEY", "PLLUM_API_KEY"]
    missing_secrets = []
    
    for secret in required_secrets:
        if not os.environ.get(secret):
            missing_secrets.append(secret)
    
    if missing_secrets:
        return jsonify({
            "status": "missing_secrets",
            "missing": missing_secrets
        })
    
    return jsonify({
        "status": "all_secrets_available",
        "message": "All required secrets are available"
    })

@app.route('/')
def index():
    """Render the web interface for the Discord bot"""
    config = get_config_details()
    
    html_head = """
    <!DOCTYPE html>
    <html lang="en" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PLLuM Discord Bot</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Function to check bot status
            function checkBotStatus() {
                fetch('/api/bot-status')
                    .then(function(response) { return response.json(); })
                    .then(function(data) {
                        const statusBox = document.getElementById('bot-status-box');
                        const statusTitle = document.getElementById('bot-status-title');
                        const statusMessage = document.getElementById('bot-status-message');
                        const statusError = document.getElementById('bot-status-error');
                        const statusTime = document.getElementById('bot-status-time');
                        
                        // Update status box
                        if (data.is_running) {
                            statusBox.className = "p-3 mb-4 bg-body-tertiary rounded-3 border-start border-success border-5";
                            statusTitle.textContent = "Status: Active";
                        } else {
                            statusBox.className = "p-3 mb-4 bg-body-tertiary rounded-3 border-start border-warning border-5";
                            statusTitle.textContent = "Status: Inactive";
                        }
                        
                        // Update error message if any
                        if (data.error) {
                            statusError.textContent = "Error: " + data.error;
                            statusError.classList.remove('d-none');
                        } else {
                            statusError.classList.add('d-none');
                        }
                        
                        // Update last check time
                        statusTime.textContent = "Last updated: " + data.last_check;
                    })
                    .catch(function(error) {
                        console.error('Error checking bot status:', error);
                    });
            }
            
            // Function to start the bot
            function startBot() {
                const startBtn = document.getElementById('start-bot-btn');
                startBtn.disabled = true;
                startBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Starting...';
                
                fetch('/api/start-bot', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    console.log('Bot start response:', data);
                    
                    // Show toast notification
                    if (data.status === 'success') {
                        showToast('Bot Starting', 'The bot is starting up. This may take a few moments.', 'success');
                    } else if (data.status === 'warning') {
                        showToast('Already Running', data.message, 'warning');
                    } else {
                        showToast('Error', data.message || 'Failed to start the bot', 'danger');
                    }
                    
                    // Re-enable button and update status
                    startBtn.disabled = false;
                    startBtn.innerHTML = 'Start Bot';
                    checkBotStatus();
                })
                .catch(function(error) {
                    console.error('Error starting bot:', error);
                    showToast('Error', 'Failed to start the bot: ' + error, 'danger');
                    startBtn.disabled = false;
                    startBtn.innerHTML = 'Start Bot';
                });
            }
            
            // Function to check available secrets
            function checkSecrets() {
                const secretsBtn = document.getElementById('check-secrets-btn');
                secretsBtn.disabled = true;
                secretsBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Checking...';
                
                fetch('/api/check-secrets')
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    console.log('Secrets check response:', data);
                    
                    // Re-enable button
                    secretsBtn.disabled = false;
                    secretsBtn.innerHTML = 'Check Secrets';
                    
                    // Show result
                    if (data.status === 'all_secrets_available') {
                        showToast('Secrets Check', 'All required secrets are available.', 'success');
                    } else if (data.status === 'missing_secrets') {
                        showToast('Missing Secrets', 'Missing keys: ' + data.missing.join(', '), 'warning');
                    }
                })
                .catch(function(error) {
                    console.error('Error checking secrets:', error);
                    showToast('Error', 'Failed to check secrets: ' + error, 'danger');
                    secretsBtn.disabled = false;
                    secretsBtn.innerHTML = 'Check Secrets';
                });
            }
            
            // Function to show toast notification
            function showToast(title, message, type = 'info') {
                // Create container if it doesn't exist
                let toastContainer = document.getElementById('toast-container');
                if (!toastContainer) {
                    toastContainer = document.createElement('div');
                    toastContainer.id = 'toast-container';
                    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
                    document.body.appendChild(toastContainer);
                }
                
                // Create unique ID
                const toastId = 'toast-' + Date.now();
                
                // Create toast
                const toastHtml = `
                <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="toast-header bg-${type} bg-opacity-25">
                        <strong class="me-auto">${title}</strong>
                        <small>${new Date().toLocaleTimeString()}</small>
                        <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                    <div class="toast-body">
                        ${message}
                    </div>
                </div>`;
                
                // Add toast to container
                toastContainer.innerHTML += toastHtml;
                
                // Initialize and show the toast
                const toastElement = document.getElementById(toastId);
                const bsToast = new bootstrap.Toast(toastElement, {
                    autohide: true,
                    delay: 5000
                });
                bsToast.show();
                
                // Remove toast after hiding
                toastElement.addEventListener('hidden.bs.toast', function() {
                    toastElement.remove();
                });
            }
            
            // Check status on page load and every 30 seconds
            document.addEventListener('DOMContentLoaded', function() {
                // Initialize status checking
                checkBotStatus();
                setInterval(checkBotStatus, 30000);
                
                // Set up button event listeners
                document.getElementById('start-bot-btn').addEventListener('click', startBot);
                document.getElementById('check-secrets-btn').addEventListener('click', checkSecrets);
            });
        </script>
    </head>
    """
    
    return f"""{html_head}
    <body>
        <div class="container py-4">
            <header class="pb-3 mb-4 border-bottom">
                <div class="d-flex align-items-center text-body-emphasis text-decoration-none">
                    <img src="https://raw.githubusercontent.com/huggingface/huggingface-brand/main/assets/01_horizontal/Hugging_Face/01_horizontal_Hugging_Face_logo-noborder.svg" width="40" class="me-2" alt="Hugging Face Logo">
                    <span class="fs-4 fw-bold">PLLuM Discord Bot</span>
                </div>
            </header>

            <div id="bot-status-box" class="p-3 mb-4 bg-body-tertiary rounded-3 border-start border-secondary border-5">
                <div class="container-fluid">
                    <h2 id="bot-status-title" class="display-6 fw-bold">Status: Checking...</h2>
                    <p id="bot-status-message" class="fs-5">The Discord bot is running separately from this web interface.</p>
                    <p id="bot-status-error" class="text-danger d-none"></p>
                    <p>To interact with the bot, use Discord and the commands listed below.</p>
                    <div class="d-flex gap-2 mt-3">
                        <button id="start-bot-btn" type="button" class="btn btn-primary">Start Bot</button>
                        <button id="check-secrets-btn" type="button" class="btn btn-outline-secondary">Check Secrets</button>
                    </div>
                    <p id="bot-status-time" class="text-muted small mt-2"></p>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="h-100 p-4 bg-body-tertiary border rounded-3">
                        <h3>Configuration</h3>
                        <ul class="list-group list-group-flush bg-transparent">
                            <li class="list-group-item d-flex justify-content-between align-items-center bg-transparent">
                                Model ID
                                <span class="badge bg-primary rounded-pill">{config["model"]}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between align-items-center bg-transparent">
                                Command Prefix
                                <span class="badge bg-primary rounded-pill">{config["prefix"]}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between align-items-center bg-transparent">
                                Max Tokens
                                <span class="badge bg-primary rounded-pill">{config["max_tokens"]}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between align-items-center bg-transparent">
                                Temperature
                                <span class="badge bg-primary rounded-pill">{config["temperature"]}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between align-items-center bg-transparent">
                                History Length
                                <span class="badge bg-primary rounded-pill">{config["history_length"]} messages</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between align-items-center bg-transparent">
                                Conversation Timeout
                                <span class="badge bg-primary rounded-pill">{config["timeout"]} seconds</span>
                            </li>
                        </ul>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="h-100 p-4 bg-body-tertiary border rounded-3">
                        <h3>Features</h3>
                        <div class="feature-list">
                            <div class="d-flex align-items-start mb-3">
                                <div class="p-2 me-3 bg-primary bg-opacity-25 rounded">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-robot" viewBox="0 0 16 16">
                                        <path d="M6 12.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5ZM3 8.062C3 6.76 4.235 5.765 5.53 5.886a26.58 26.58 0 0 0 4.94 0C11.765 5.765 13 6.76 13 8.062v1.157a.933.933 0 0 1-.765.935c-.845.147-2.34.346-4.235.346-1.895 0-3.39-.2-4.235-.346A.933.933 0 0 1 3 9.219V8.062Zm4.542-.827a.25.25 0 0 0-.217.068l-.92.9a24.767 24.767 0 0 1-1.871-.183.25.25 0 0 0-.068.495c.55.076 1.232.149 2.02.193a.25.25 0 0 0 .189-.071l.754-.736.847 1.71a.25.25 0 0 0 .404.062l.932-.97a25.286 25.286 0 0 0 1.922-.188.25.25 0 0 0-.068-.495c-.538.074-1.207.145-1.98.189a.25.25 0 0 0-.166.076l-.754.785-.842-1.7a.25.25 0 0 0-.182-.135Z"/>
                                        <path d="M8.5 1.866a1 1 0 1 0-1 0V3h-2A4.5 4.5 0 0 0 1 7.5V8a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1v1a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1a1 1 0 0 0 1-1V9a1 1 0 0 0-1-1v-.5A4.5 4.5 0 0 0 10.5 3h-2V1.866ZM14 7.5V13a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V7.5A3.5 3.5 0 0 1 5.5 4h5A3.5 3.5 0 0 1 14 7.5Z"/>
                                    </svg>
                                </div>
                                <div>
                                    <h5>AI-Powered Chat</h5>
                                    <p class="mb-0">Chat with the PLLuM AI through Discord using the power of the Hugging Face API.</p>
                                </div>
                            </div>
                            <div class="d-flex align-items-start mb-3">
                                <div class="p-2 me-3 bg-primary bg-opacity-25 rounded">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-chat-dots" viewBox="0 0 16 16">
                                        <path d="M5 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm4 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 1a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/>
                                        <path d="m2.165 15.803.02-.004c1.83-.363 2.948-.842 3.468-1.105A9.06 9.06 0 0 0 8 15c4.418 0 8-3.134 8-7s-3.582-7-8-7-8 3.134-8 7c0 1.76.743 3.37 1.97 4.6a10.437 10.437 0 0 1-.524 2.318l-.003.011a10.722 10.722 0 0 1-.244.637c-.079.186.074.394.273.362a21.673 21.673 0 0 0 .693-.125zm.8-3.108a1 1 0 0 0-.287-.801C1.618 10.83 1 9.468 1 8c0-3.192 3.004-6 7-6s7 2.808 7 6c0 3.193-3.004 6-7 6a8.06 8.06 0 0 1-2.088-.272 1 1 0 0 0-.711.074c-.387.196-1.24.57-2.634.893a10.97 10.97 0 0 0 .398-2z"/>
                                    </svg>
                                </div>
                                <div>
                                    <h5>Context-Aware Conversations</h5>
                                    <p class="mb-0">The bot remembers your conversation history for more coherent responses.</p>
                                </div>
                            </div>
                            <div class="d-flex align-items-start mb-3">
                                <div class="p-2 me-3 bg-primary bg-opacity-25 rounded">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-gear" viewBox="0 0 16 16">
                                        <path d="M8 4.754a3.246 3.246 0 1 0 0 6.492a3.246 3.246 0 0 0 0-6.492zM5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0z"/>
                                        <path d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52l-.094-.319zm-2.633.283c.246-.835 1.428-.835 1.674 0l.094.319a1.873 1.873 0 0 0 2.693 1.115l.291-.16c.764-.415 1.6.42 1.184 1.185l-.159.292a1.873 1.873 0 0 0 1.116 2.692l.318.094c.835.246.835 1.428 0 1.674l-.319.094a1.873 1.873 0 0 0-1.115 2.693l.16.291c.415.764-.42 1.6-1.185 1.184l-.291-.159a1.873 1.873 0 0 0-2.693 1.116l-.094.318c-.246.835-1.428.835-1.674 0l-.094-.319a1.873 1.873 0 0 0-2.692-1.115l-.292.16c-.764.415-1.6-.42-1.184-1.185l.159-.291A1.873 1.873 0 0 0 1.945 8.93l-.319-.094c-.835-.246-.835-1.428 0-1.674l.319-.094A1.873 1.873 0 0 0 3.06 4.377l-.16-.292c-.415-.764.42-1.6 1.185-1.184l.292.159a1.873 1.873 0 0 0 2.692-1.115l.094-.319z"/>
                                    </svg>
                                </div>
                                <div>
                                    <h5>Multiple Command Options</h5>
                                    <p class="mb-0">Use single commands or engage in full conversations with the bot.</p>
                                </div>
                            </div>
                            <div class="d-flex align-items-start">
                                <div class="p-2 me-3 bg-primary bg-opacity-25 rounded">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-translate" viewBox="0 0 16 16">
                                        <path d="M4.545 6.714 4.11 8H3l1.862-5h1.284L8 8H6.833l-.435-1.286H4.545zm1.634-.736L5.5 3.956h-.049l-.679 2.022H6.18z"/>
                                        <path d="M0 2a2 2 0 0 1 2-2h7a2 2 0 0 1 2 2v3h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-3H2a2 2 0 0 1-2-2V2zm2-1a1 1 0 0 0-1 1v7a1 1 0 0 0 1 1h7a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H2zm7.138 9.995c.193.301.402.583.63.846-.748.575-1.673 1.001-2.768 1.292.178.217.451.635.555.867 1.125-.359 2.08-.844 2.886-1.494.777.665 1.739 1.165 2.93 1.472.133-.254.414-.673.629-.89-1.125-.253-2.057-.694-2.82-1.284.681-.747 1.222-1.651 1.621-2.757H14V8h-3v1.047h.765c-.318.844-.74 1.546-1.272 2.13a6.066 6.066 0 0 1-.415-.492 1.988 1.988 0 0 1-.94.31z"/>
                                    </svg>
                                </div>
                                <div>
                                    <h5>Multi-Language Support</h5>
                                    <p class="mb-0">Automatically detects Polish and English, with response formatting to match your language.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-md-12">
                    <div class="p-4 bg-body-tertiary border rounded-3">
                        <h3>Available Commands</h3>
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Command</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><code>{config["prefix"]}help</code></td>
                                        <td>Shows the help message with all available commands</td>
                                    </tr>
                                    <tr>
                                        <td><code>{config["prefix"]}ask &lt;question&gt;</code></td>
                                        <td>Ask PLLuM AI a one-time question</td>
                                    </tr>
                                    <tr>
                                        <td><code>{config["prefix"]}chat</code></td>
                                        <td>Start a conversation with PLLuM AI</td>
                                    </tr>
                                    <tr>
                                        <td><code>{config["prefix"]}end</code></td>
                                        <td>End your current conversation</td>
                                    </tr>
                                    <tr>
                                        <td><code>{config["prefix"]}ping</code></td>
                                        <td>Check the bot's latency</td>
                                    </tr>
                                    <tr>
                                        <td><code>{config["prefix"]}info</code></td>
                                        <td>Get information about the bot</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        
                        <h3 class="mt-4">Administrative Commands</h3>
                        <p>These commands are only available to server administrators and owners:</p>
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Command</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><code>{config["prefix"]}admin channels</code></td>
                                        <td>Manage channels where the bot can respond</td>
                                    </tr>
                                    <tr>
                                        <td><code>{config["prefix"]}admin roles</code></td>
                                        <td>Manage roles that can use the bot</td>
                                    </tr>
                                    <tr>
                                        <td><code>{config["prefix"]}admin prefix</code></td>
                                        <td>Set a custom command prefix for your server</td>
                                    </tr>
                                    <tr>
                                        <td><code>{config["prefix"]}admin model</code></td>
                                        <td>Set the AI model for your server</td>
                                    </tr>
                                    <tr>
                                        <td><code>{config["prefix"]}admin settings</code></td>
                                        <td>View current server settings</td>
                                    </tr>
                                    <tr>
                                        <td><code>{config["prefix"]}admin reset</code></td>
                                        <td>Reset all server settings to defaults</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <div class="p-4 mb-4 bg-body-tertiary rounded-3 border">
                <h3>How to Use</h3>
                <ol class="list-group list-group-numbered mb-0">
                    <li class="list-group-item d-flex justify-content-between align-items-start bg-transparent border-0">
                        <div class="ms-2 me-auto">
                            <div class="fw-bold">Invite the bot to your Discord server</div>
                            Use the OAuth2 URL from the Discord Developer Portal
                        </div>
                    </li>
                    <li class="list-group-item d-flex justify-content-between align-items-start bg-transparent border-0">
                        <div class="ms-2 me-auto">
                            <div class="fw-bold">See all available commands</div>
                            Type <code>{config["prefix"]}help</code> in any channel where the bot has access
                        </div>
                    </li>
                    <li class="list-group-item d-flex justify-content-between align-items-start bg-transparent border-0">
                        <div class="ms-2 me-auto">
                            <div class="fw-bold">Start interacting with PLLuM AI</div>
                            Use <code>{config["prefix"]}chat</code> to start a conversation or <code>{config["prefix"]}ask</code> for one-time questions
                        </div>
                    </li>
                    <li class="list-group-item d-flex justify-content-between align-items-start bg-transparent border-0">
                        <div class="ms-2 me-auto">
                            <div class="fw-bold">Continue your conversation</div>
                            Mention the bot or reply to its messages to continue chatting
                        </div>
                    </li>
                </ol>
            </div>
            
            <footer class="pt-3 mt-4 text-body-secondary border-top">
                PLLuM AI Discord Bot &copy; {datetime.now().year}
            </footer>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
