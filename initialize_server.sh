
python --version;

echo "Installing Virtualenv into the system ";
pip install virtualenv;

echo "Installing Virtualenv Wrapper into the system ";
pip install virtualenvwrapper-win;

echo "Creating Virtualenv";
mkvirtualenv minipjt ; 

pip install -r requirements.txt





echo "RUN: 'C:\Users\Lenovo\Envs\minipj\Scripts\activate' to activate project environment..." ;
set /p DUMMY=Hit ENTER to Continue...


python manage.py migrate
python manage.py runserver



