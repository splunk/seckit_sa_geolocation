if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    export OS=$NAME
else
    echo "Unable to find linux OS"
    exit 0
fi

echo "Linux OS : $OS"

if [[ "$OS" == *"Red Hat"* ]]; then
    microdnf install yum
    yum -y update
    yum -y install zlib-devel bzip2 bzip2-devel sqlite sqlite-devel openssl-devel \
    xz xz-devel libffi-devel findutils git gcc make
    yum -y install java-11-openjdk-devel
elif [[ "$OS" == *"Debian"* ]]; then
    apt update
    apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libffi-dev liblzma-dev python-openssl git gcc make
fi

cd /home/circleci/work_backend

if [ -f "${TEST_SET}/pytest-ci.ini" ]; then
    cp -f ${TEST_SET}/pytest-ci.ini pytest.ini
fi

if ! command -v pyenv &> /dev/null
then
    if [ ! -d "~/.pyenv" ]; then
        echo "Installing pyenv"
        curl https://pyenv.run | bash
    fi
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
fi

python2=$(/opt/splunk/bin/splunk cmd python2 -V 2>&1) 
python3=$(/opt/splunk/bin/splunk cmd python3 -V)

if [[ "$python3" == *"Python 3."* ]]; then
    echo "Installing $python3"
    python_version=$(echo $python3| cut -d' ' -f 2)
    pyenv install -s "$python_version"
    pyenv global "$python_version"
    pip3 install pytest --target=py3
    pip3 install pytest-expect --target=py3
    pip3 install git+https://github.com/rfaircloth-splunk/agent-python-pytest.git --target=py3
    pyenv versions
fi

if [[ "$python2" == *"Python 2."* ]]; then
    echo "Installing $python2"
    python_version=$(echo $python2| cut -d' ' -f 2)
    pyenv install -s "$python_version"
    pyenv global "$python_version"
    pip2 install pytest --target=py2
    pip2 install pytest-expect --target=py2
    pyenv versions
fi

source /opt/splunk/bin/setSplunkEnv

export test_exit_code_py2=0
export test_exit_code_py3=0

if [ -d "py2" ]; then
    cd py2
    echo "Executing Test..."
    python2 -m pytest -v ../${TEST_SET} --junitxml=/home/circleci/work_backend/test-results/test_py2.xml
    test_exit_code_py2=$?
    cd ..
fi

if [ -d "py3" ]; then
    cd py3
    echo "Executing Test..."
    echo Test Args $@ --reportportal -o "rp_endpoint=${RP_ENDPOINT}" -o "rp_launch_attributes=${RP_LAUNCH_ATTRIBUTES}" \
    -o "rp_project=${RP_PROJECT}" -o "rp_launch=${RP_LAUNCH}" -o "rp_launch_description='${RP_LAUNCH_DESC}'" -o "rp_ignore_attributes='xfail' 'usefixture'" \
    ${TEST_SET}
    python3 -m pytest -v -p pytest_reportportal ../${TEST_SET} --junitxml=/home/circleci/work_backend/test-results/test_py3.xml \
    --reportportal -o "rp_endpoint=${RP_ENDPOINT}" -o "rp_launch_attributes=${RP_LAUNCH_ATTRIBUTES}" \
    -o "rp_project=${RP_PROJECT}" -o "rp_launch=${RP_LAUNCH}" -o "rp_launch_description='${RP_LAUNCH_DESC}'" -o "rp_ignore_attributes='xfail' 'usefixture'"
    test_exit_code_py3=$?
    cd ..
fi

if [[ $test_exit_code_py2 == 0 && $test_exit_code_py3 == 0 ]]; then 
    exit "$test_exit_code_py2" 
elif [[ $test_exit_code_py2 != 0 ]]; then
    exit "$test_exit_code_py2"
else
    exit "$test_exit_code_py3"
fi