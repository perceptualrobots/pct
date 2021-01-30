#!/bin/bash

nbdev_clean_nbs
nbdev_build_lib
#nbdev_diff_nbs
nbdev_test_nbs
nbdev_build_docs


git add -A
git commit -m update
#git push

