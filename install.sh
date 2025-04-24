#!/bin/bash
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install it and try again."
    sudo apt-get install python3
fi

# Check if the version is specifically Python 3.12
REQUIRED_VERSION="3.12"
if ! [[ $(echo -e "$PYTHON_VERSION\n$REQUIRED_VERSION" | sort -V | head -n1) == "$REQUIRED_VERSION" ]]; then
    echo "Python 3.12 or greater is required. Detected version: $PYTHON_VERSION"
    exit 1
fi

echo "Python 3.12 or greater detected. Proceeding with installation..."



# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip is not installed. Installing pip..."
    sudo apt-get install python3-pip
fi

python3 -m pip install --upgrade setuptools


# Check if pip is up to date
PIP_VERSION=$(pip3 --version 2>&1 | awk '{print $2}')
if ! [[ $(echo -e "$PIP_VERSION\n$REQUIRED_VERSION" | sort -V | head -n1) == "$REQUIRED_VERSION" ]]; then
    echo "pip is not up to date. Updating pip..."
    python3 -m pip install --upgrade pip
fi

# Ask the user if they want to use a virtual environment
read -p "Do you want to use a virtual environment? (y/n): " USE_VENV

if [[ "$USE_VENV" == "y" || "$USE_VENV" == "Y" ]]; then
    # Check if virtualenv is installed
    if ! command -v virtualenv &> /dev/null; then
        echo "virtualenv is not installed. Installing virtualenv..."
        python3 -m pip install virtualenv
    fi

    # Create a virtual environment
    echo "Creating a virtual environment..."
    VENV_DIR="venv"
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv $VENV_DIR
    else
        echo "Virtual environment already exists. Skipping creation."
    fi

    # Activate the virtual environment
    echo "Activating the virtual environment..."
    source $VENV_DIR/bin/activate
else
    echo "Proceeding without a virtual environment..."
fi

# Install required packages
echo "Installing required packages..."
python3 -m pip install -r requirements.txt



