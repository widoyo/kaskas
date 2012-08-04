# -*- coding: utf-8 -*-
"""
sakulaci.views.kas

"""
import os
from flask import Blueprint, request, render_template

kas = Blueprint('kas', __name__)

@kas.route('/')
def index():
    return render_template("kas/index.html")
