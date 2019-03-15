# docker-apps [WIP]

Generator for various standard stack in docker, first attempted to do it with ansible, it seems more efficient to just generate apps and stacks with pure python.

## Purpose

The goal of this simple generator is to be able to generate images for various apps easily, and offer a flexible architecture to build tailored custom docker images.
It is mainly useful to quickly deploy simple apps and/or work on dev version of those ones.

There are apps and stacks, apps are usually some app/software that are deployed on top of some systems. stacks are basically relying on docker-compose.

## Requirements

This generator is based on python

    mkvirtualenv --python=`which python3` docker-apps

Install dependencies with
    pip install -r requirements.txt


## How it works

Edit the myconfig.yml file to define your recipes for both apps and stacks, they are refereing either bases, apsp or flavors. Each recipe could have one base, one main app and several flavors. Flavors are common docker set of commands that should be independant from bases and apps as much as possible.

License
-------

MIT
