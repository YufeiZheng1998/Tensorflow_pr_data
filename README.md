# Tensorflow_pr_data
This repo is used for 18668 team project, the data is collected through PyGithub. 
tensorflow_sample.csv is just a small sample, please download the full dataset from 
https://18668-teamproject.s3.us-west-2.amazonaws.com/tensorflow_full.csv

# Data Schema

## pr_id 
ID of the PR

## pr_title
Title of the PR

## pr_body
PR's description

## requester
Who request the PR review

## pr_commenters

All people who comment the PR

## pr_comments
All comments for the PR, merged to a list object

## original_reviewers
The *requested* for this PR

## active_reviewers
The requested reviewers for the PR and the status is "approved", "request_changes"..

## assignees
Assignees for the PR

## changed_file_content
Merged files changes for the PR

## commits_messages
Merged commit description for each commits for the PR

## commits_comments
Merged comment messages for each commit in the PR

## created_at
PR creation time
