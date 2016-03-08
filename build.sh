#/usr/bin/env bash

build() {
    echo 'Building ...'
    bundle exec jekyll build
    echo 'Minifying markup ...'
    # Replace multiple whitespace, including newline, with one space.
    # Remove trailing whitespace.
    for f in $(find _site -regextype posix-extended -regex '.*\.(html|xml|json)'); do
        perl -0777 -pi -e 's/[ \n]+/ /g; s/[ ]+$//' $f
    done
}

deploy() {
    echo "Deploying ..."
}

if [ $# -eq 0 ]; then
    build
elif [ "$1" = 'deploy' ]; then
    build
    deploy
fi
