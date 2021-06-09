#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 11 15:06:49 2021

@author: Ilyas
"""

import sarouty_scraper
import pandas as pd

listings = get_listings(200)
listings.to_csv('listings.csv',encoding = 'utf-8',index=False)
