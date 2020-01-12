#!/bin/sh
hugo --theme=hugo_theme_robust_modified
git add docs/
git commit -m "rebuild"
git push
