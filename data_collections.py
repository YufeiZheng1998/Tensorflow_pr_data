import requests
from github import Github
from github.GithubException import RateLimitExceededException
import csv
import logging
import calendar
import time

csv_columns = ['pr_id','pr_title','pr_body', 'requester', 'pr_commenters', 'pr_comments', 'original_reviewers', 'active_reviewers', 'assignees', 'changed_files_content','commits_messages','commits_comments','created_at']
csv_file = "tensorflow_sample.csv"
g = Github("YOUR_GITHUB_TOKEN")
repo = g.get_repo("tensorflow/tensorflow")
closed_prs = iter(repo.get_pulls(state='closed'))
with open(csv_file, 'a+') as csvfile:
  cnt = 0
  writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
  writer.writeheader()
  while True:
    try:
      pr = next(closed_prs)
      cnt += 1
      print("Start Processing PR: {}".format(cnt))
      pr_data = {}
      pr_data['pr_id'] = pr.number
      pr_data['pr_title'] = pr.title
      pr_data['pr_body'] = pr.body
      pr_data['requester'] = pr.user.login
      r_comments = pr.get_review_comments()
      i_comments = pr.get_issue_comments()
      all_commenters = set()
      comment_docs = []
      
      for r_comment in r_comments:
        if r_comment.user != None and 'bot' not in r_comment.user.login:
          reviewer = r_comment.user.login
          comment_docs.append(r_comment.body)
          all_commenters.add(reviewer)
      
      for i_comment in i_comments:
        if i_comment.user != None and 'bot' not in i_comment.user.login:
          reviewer = i_comment.user.login
          all_commenters.add(reviewer)
          comment_docs.append(i_comment.body)

      pr_data['pr_commenters'] = list(all_commenters)
      pr_data['pr_comments'] = comment_docs
      # TODO: find reviewers list
      reviews = pr.get_reviews()
      original_reviewers = []
      active_reviewers = []
      for review in reviews:
        original_reviewers.append(review.user.login)
        if review.state == 'COMMENTED' or review.state == 'APPROVED' or review.state == 'CHANGES_REQUESTED':
          active_reviewers.append(review.user.login)

      pr_data['original_reviewers'] = original_reviewers
      pr_data['active_reviewers'] = active_reviewers
      pr_assignees = []
      for assignee in pr.assignees:
        pr_assignees.append(assignee.login)
      pr_data['assignees'] = pr_assignees
      
      # Process changed files
      pr_data['changed_files_content'] = requests.get(pr.diff_url).content
      # Commmit Messages
      commits_messages = []
      commits_comments = []
      for commit in pr.get_commits():
        commits_messages.append(commit.commit.message)
        commit_comments =  commit.get_comments()
        for comment in commit_comments:
          commits_comments.append(comment.body)
      pr_data['commits_messages'] = commits_messages
      pr_data['commits_comments'] = commits_comments
      # Add time related field
      pr_data['created_at'] = pr.created_at
      writer.writerow(pr_data)
    except StopIteration:
      print("finished!!!")
      break
    except RateLimitExceededException:
      search_rate_limit = g.get_rate_limit().search
      logging.info('search remaining: {}'.format(search_rate_limit.remaining))
      reset_timestamp = calendar.timegm(search_rate_limit.reset.timetuple())
      sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 10
      logging.info("Hit Rate Limit: sleep {}".format(sleep_time))
      time.sleep(sleep_time)
      continue
