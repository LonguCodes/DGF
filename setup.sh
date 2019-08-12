rm -rf dist
if [ -n "$1" ]; then
    echo $1 > VERSION
fi
python setup.py sdist bdist_wheel
twine upload dist/*