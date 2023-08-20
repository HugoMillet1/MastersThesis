# MastersThesis

This repository is my work produced in my Master's Thesis dissertation at Heriot-Watt University Edinburgh. Its goal was to set a neurorobotic model where a simulated brain network and an iCub robot simulation would exchange information to replicate symptoms of Parkinson's Disease, while exploring a treatment for it known as closed-loop Deep Brain Stimulation (DBS).
To use this repo, you will need :

- The complete files and package requirements specified in "requirements.txt" of the brain "Marmoset Model", developped by Dr. Ranieri (https://ieeexplore.ieee.org/document/9524925)
- The robotology-superbuild package, to use the iCub robot (https://github.com/robotology/robotology-superbuild)

This repo is composed of :

- MarmosetBG.py & GenericBG.py : The main programs of the brain Marmoset model of Dr. Ranieri, modified by me, in order to add the necessary data processing, along with the closed-loop DBS protocol.
- controle_exp.py : The program which controls the iCub robot simulation, making it realize cycles of pronosupination while generating tremors related to the intensity of the Parkinson's Disease in the brain model
- icub_world.sdf : The 3D Gazebo simulation of the iCub robot (it is already present in the robotology superbuild package but was duplicated and renamed here)

The results were made using Python3.8 for the brain model and Python 3.10 for the robot control.
To make the ensemble of the programs functions, apply this serie of steps :

Launch yarpserver in a terminal :

'''console
yarpserver
'''

On another terminal, launch the iCub robot Gazebo simulation :

'''console
gazebo icub_world.sdf
'''
On another terminal, launch the brain Marmoset model :

'''console
python3.8 MarmosetBG.py
'''

If the part of code enabling communication with the robot program is not commented, the simulation will wait to connect to the robot program before launching. Therefore, launch it in another terminal with :

'''console
python3.10 controle_exp.py
'''

