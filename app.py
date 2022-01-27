from flask import Flask, render_template, request, flash, redirect, session, g,abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError