# MastersThesis

This repository is my work produced in my Master's Thesis dissertation at Heriot-Watt University Edinburgh. Its goal was to set a neurorobotic model where a simulated brain network and an iCub robot simulation would exchange information to replicate symptoms of Parkinson's Disease, while exploring a treatment for it known as closed-loop Deep Brain Stimulation (DBS).
To use this repo, you will need :

- The complete files and package requirements specified in "requirements.txt" of the brain "Marmoset Model", developped by Dr. Ranieri (https://ieeexplore.ieee.org/document/9524925)
- The robotology-superbuild package, to use the iCub robot (https://github.com/robotology/robotology-superbuild)

This repo is composed of :

- MarmosetBG.py & GenericBG.py : The main programs of the brain Marmoset model of Dr. Ranieri, modified by me, in order to add the necessary data processing, along with the closed-loop DBS protocol.
- controle_exp.py : The program which controls the iCub robot simulation, making it realize cycles of pronosupination while generating tremors related to the intensity of the Parkinson's Disease in the brain model
- icub_world.sdf : The 3D simulation of the iCub robot (it is already present in the robotology superbuild package but was duplicated and renamed here)
