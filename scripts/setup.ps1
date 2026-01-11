# PowerShell script for Quantum Capital Platform Setup

Write-Host "Starting Quantum Capital Platform setup..."

# Define paths relative to the script's location
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = $scriptDir # The project root is now the current directory (emphasis)
$backendDir = Join-Path $projectRoot "backend"
$frontendDir = Join-Path $projectRoot "frontend"
$backendRequirements = Join-Path $backendDir "requirements.txt"

# --- Backend Setup (Django) ---
Write-Host "\n--- Setting up Backend (Django) ---"
Set-Location $backendDir

# Create and activate Python virtual environment
Write-Host "Creating Python virtual environment..."
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install Python dependencies
Write-Host "Installing Python dependencies..."
Write-Host "Current directory: $(pwd)"
Write-Host "Checking for requirements.txt:"
Get-Item $backendRequirements -ErrorAction SilentlyContinue | ForEach-Object { Write-Host "Found: $($_.FullName)" }

Try {
    pip install -r $backendRequirements -v
} Catch {
    Write-Error "Failed to install Python dependencies. This might be due to missing build tools (e.g., for Pillow)."
    Write-Error "On Windows, ensure you have 'Build Tools for Visual Studio' with 'Desktop development with C++' installed, or try `pip install --no-binary :all: Pillow==10.1.0` if that doesn't work."
    Exit 1
}

# Create Django migrations
Write-Host "Creating Django migrations..."
Try {
    python manage.py makemigrations users
    python manage.py migrate
} Catch {
    Write-Error "Failed to create or apply Django migrations. Ensure the PostgreSQL database is running and configured correctly in .env, and manage.py exists."
    Exit 1
}

# Go back to the root directory after backend setup
Set-Location $projectRoot

Write-Host "Backend setup complete."

# --- Frontend Setup (React) ---
Write-Host "\n--- Setting up Frontend (React) ---"
Set-Location $frontendDir

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..."
Try {
    npm install
} Catch {
    Write-Error "Failed to install Node.js dependencies. Ensure Node.js and npm are installed."
    Exit 1
}

Set-Location $projectRoot

Write-Host "Frontend setup complete."

Write-Host "\nQuantum Capital Platform setup finished successfully!"
Write-Host "\nNext steps:"
Write-Host "1. Ensure PostgreSQL is running and the 'quantum_capital_db' database is created with appropriate user permissions."
Write-Host "2. Open a new terminal. (IMPORTANT: Run as Administrator)"
Write-Host "3. Navigate to the project root directory: cd D:\PROJECTS\emphasis"
Write-Host "4. Navigate to the backend directory: cd backend"
Write-Host "5. Activate the virtual environment: .\venv\Scripts\Activate.ps1"
Write-Host "6. Run the Django development server: python manage.py runserver"
Write-Host "7. In another terminal, navigate to the frontend directory: cd frontend"
Write-Host "8. Run the React development server: npm start"
