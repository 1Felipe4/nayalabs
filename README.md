
# Nayalabs Django Application Setup

This guide provides instructions to set up the Nayalabs Django application on both Windows and Linux.

## Prerequisites

Ensure you have the following installed:
- Python 3.x
- Git

## Cloning the Repository

1. Open your terminal or command prompt.
2. Clone the repository using the following command:

   ```bash
   git clone git@github.com:1Felipe4/nayalabs.git
   ```

3. Navigate to the project directory:

   ```bash
   cd nayalabs
   ```

## Setting Up a Virtual Environment

### On Windows:

1. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:

   ```bash
   venv\Scripts\activate
   ```

### On Linux:

1. Create a virtual environment:

   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:

   ```bash
   source venv/bin/activate
   ```

## Installing Dependencies

With the virtual environment activated, install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Django Application

1. Start the Django development server:

   ```bash
   python manage.py runserver
   ```

2. Open your web browser and go to:

   ```
   http://localhost:8000
   ```

3. Login with the following credentials:

   - **Username:** user
   - **Password:** user

## Notes

- Ensure the virtual environment is activated whenever you work on this project.
- Use `CTRL + C` in the terminal to stop the server when you're done.

## Troubleshooting

- If you encounter any issues, ensure all dependencies are installed and that the virtual environment is active.
- For Windows users, if activating the virtual environment fails, ensure you are running the command prompt with administrator privileges.

## Contributing

Feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License.
