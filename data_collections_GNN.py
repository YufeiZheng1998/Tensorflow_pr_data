import requests
from github import Github
from github.GithubException import RateLimitExceededException, UnknownObjectException
import csv
import logging
import calendar
import time

csv_columns = ['pr_id','pr_title','pr_body', 'requester', 'pr_commenters', 'pr_comments', 'active_reviewers', 'commits_messages','changed_files']
csv_file = "tensorflow_sample.csv"
g = Github("YOUR_GITHUBTOKEN")
repo = g.get_repo("tensorflow/tensorflow")
with open(csv_file, 'a+') as csvfile:
  pr_number = 1
  writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
  writer.writeheader()
  while True:
    try:
      print("Start Processing PR: {}".format(pr_number))
      pr_data = {}
      pr = repo.get_pull(pr_number)
      if pr.state != 'closed':
        pr_number += 1
        continue
      pr_number += 1
      if pr_number == 40000:
        break
      # Processing active reviewers
      # Reviewer whose review status is "COMMENTED", "APPROVED" or 'CHANGES_REQUESTED'
      reviews = pr.get_reviews()
      active_reviewers = set()
      for review in reviews:
        if review.state == 'COMMENTED' or review.state == 'APPROVED' or review.state == 'CHANGES_REQUESTED':
          active_reviewers.add(review.user.login)
      # If no one reviews this pr, skip it.
      if len(active_reviewers) == 0:
        continue
      pr_data['active_reviewers'] = list(active_reviewers)
      
      # Processing pr related basic information
      pr_data['pr_id'] = pr.number
      pr_data['pr_title'] = pr.title
      pr_data['pr_body'] = pr.body
      pr_data['requester'] = pr.user.login

      
      r_comments = pr.get_review_comments()
      i_comments = pr.get_issue_comments()
      all_commenters = set()
      comment_docs = []
      # If the commenter is not in the list of active_reviewer, just skip.
      for r_comment in r_comments:
        if r_comment.user != None and 'bot' not in r_comment.user.login:
          reviewer = r_comment.user.login
          if reviewer not in active_reviewers:
            continue
          comment_docs.append(r_comment.body)
          all_commenters.add(reviewer)
      
      for i_comment in i_comments:
        if i_comment.user != None and 'bot' not in i_comment.user.login:
          reviewer = i_comment.user.login
          if reviewer not in active_reviewers:
            continue
          comment_docs.append(i_comment.body)
          all_commenters.add(reviewer)

      pr_data['pr_commenters'] = list(all_commenters)
      pr_data['pr_comments'] = comment_docs


      # Commmit Messages and changed_file_paths
      commits_messages = []
      commits_comments = []
      changed_files= set()
      for commit in pr.get_commits():
        commits_messages.append(commit.commit.message)
        files = commit.files
        for f in files:
          changed_files.add(f.filename)
      pr_data['commits_messages'] = commits_messages
      pr_data['changed_files'] = list(changed_files)
      writer.writerow(pr_data)

    except RateLimitExceededException:
      search_rate_limit = g.get_rate_limit().search
      logging.info('search remaining: {}'.format(search_rate_limit.remaining))
      reset_timestamp = calendar.timegm(search_rate_limit.reset.timetuple())
      sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 10
      logging.info("Hit Rate Limit: sleep {}".format(sleep_time))
      time.sleep(sleep_time)
      continue
    except UnknownObjectException:
      pr_number += 1
      continue
    except AttributeError:
      continue
