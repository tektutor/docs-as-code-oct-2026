# Day 1

## Info - For detailed Git & GitHub reference, check my public repo on GitHub
<pre>
https://github.com/tektutor/git-us-june2023-batch1.git
</pre>  

## Info - Docs as Code
<pre>
- Sphinx is a tool developed by Python community as an open source tool
- to generate Python documentation
- today Docs as Code is used by Linux Kernel, Linux Distros, Python, Automotive Industry & Semi-conductor industry
- it is supported in all Linux distributions
  - Ubuntu
  - Fedora
  - Red Hat Linux
  - SUSE Linux
- under the hood it depends on LaTex
- under the hood it depends on LaTex and many other tools like Pandoc, PlantUML, etc.,
</pre>

## Info - Git Overview
<pre>
- Git is an open source version control software developed by Linus Torvalds
- Almost the entire IT industry today uses some form of Git version control
  - example
    - GitHub
    - GitLab
    - BitBucket, etc.,
  - GitHub, GitLab, BitBucket are version control software that is developed
    on top of Git command-line tool
  - These servers acts as a remote repository with Webconsole (GUI) with some
    differentiating features
</pre>

## Lab - Git

Creating a git repository locally
```
cd ~
mkdir -p git-demo
cd git-demo
git init

ls -la
tree .git
```

Configuring your git
```
git config --global user.name "Jeganathan Swaminathan"
git config --global user.email "mailj2jegan@gmail.com"
git config --global core.editor "vim"
git config --global pull.rebase false
git config --global init.defaultBranch main
```

Listing all configs done
```
git config --global --list
git config --global --list --show-origin
git config --global user.email
```

<img width="1966" height="1191" alt="image" src="https://github.com/user-attachments/assets/8ff04f27-7460-4f5e-b04c-1ec45589fa06" />

Change or remote a setting
```
git config --global --unset core.editor
git config --global --edit
```

Git supports 3 levels
<pre>
- System - stores in /etc/gitconfig for system wide configurations for all users in that server
- Global - stores globally for a single user in ~/.gitconfig
- Local  - is the default and stores under .git/config  
</pre>


## Lab - Adding new files to the local git repo, stage and commit
Navigate to your local git repo
```
cd ~/git-demo
git status
```

Add a new file 
```
cd ~/git-demo
touch fruits
```

Check the current status of the repo
```
git status
```

Anything you wish to commit must be staged first. Hence, let's stage the file
```
git add fruits.txt
git status
```

Committing your changes in the staging area
```
git commit -m "Initial commit."
git status
```

Modify the file
```
echo "Apple" > fruits.txt
git status
```

Stage the changes done to the file
```
git add fruits.txt
```

Commit changes
```
git commit -m "Added apple to fruits"
git status
```

Checking logs
```
git log
```
<img width="1970" height="1218" alt="image" src="https://github.com/user-attachments/assets/03a09d20-ccac-44e9-aee0-0bc2c654bf25" />

## Lab - Git branch

Note
<pre>
- Branches are considered a basic feature in Git or Git variant version controls unlike the classic older version controls
  like Perforce, ClearCase, CVS, etc.,
- Branches are not copies in case of git, github or git variants
</pre>

Listing all the branches in a git repo
```
git branch
```

Creating a new branch from main branch
```
git checkout -c dev-1.0
git branch
```

Switching between branches
```
git checkout main
git branch

git checkout dev-1.0
git branch
```


Let's switch to dev-1.0 branch and make some changes
```
git checkout dev-1.0
echo "Mango" >> fruits.txt
git commit -a -m "Added Mango in dev-1.0 branch"
git log
git status
```

Let's switch back to main branch and see if those changes done in dev-1.0 are visible
```
git checkout main

# You will notice that the changes done in dev-1.0 are not visible in main branch
cat fruits.txt
```

Let's make some changes in main branch
```
echo "Orange" >> fruits.txt
git commit -a -m "Added Orange in main branch"
git log
```

Let's switch to dev-1.0 and see if the changes done in main branch are visible there
```
git checkout dev-1.0

# You will notice that the changes done in main are not visible in dev-1.0
cat fruits.txt 
```

Let's merge the changes done in main branch to the dev-1.0 branch
```
# First switch to the destination branch i.e dev-1.0 branch
git checkout dev-1.0
git branch
git merge main

# At this point, merge will create some conflicts that must be manually resolved, so edit the fruits.txt
# and resolve the merge conflicts
cat fruits.txt

# Stage the merge resolution
git add *
git commit -m "Resolve merge conflicts in dev-1.0 branch"
git status
git log
```

## Lab - GitHub commands

Cloning a remote repository to your local machine ( this is done only the first time )
```
cd ~
git clone https://github.com/tektutor/docs-as-code-oct-2026.git
cd docs-as-code-oct-2026
tree
```

Getting only delta change from remote to local repo
```
cd ~
cd docs-as-code-oct-2026
git pull
```

Delete a file from the local git repo and from local file system
```
cd ~
cd docs-as-code-oct-2026
git rm Day1/testing
```

## Info - Git pull vs fetch

Note
<pre>
- Let's assume there are 2 engineers in a team Deepa and Shankar.
- Shankar pushed a new commit to main and a new branch
- Deepa downloads his work with get fetch and can verify before merging
- Git pull does the below
  1. Download Shankar's work, without changing Deepa's files
  2. Check how far behind you are
  3. See which commits arrived
  4. See What changed in the files
  5. Take the changes into your branch, once you are happy with them
  6. Work on the new branch pushed by Shankar
- Git fetch
  - Git pull runs steps 1 to 5 in one go, i.e fetch and merge right away
  - Git fetch stops after step 1 so you can review steps 2 to 4 first 
</pre>


## Info - Sphinx
<pre>
- Sphinx is a document generator via Code
- reST - restructured text is the markup language Sphinx reads
- the file extension for reST is .rst, it is a text file that will be parsed by Sphinx tool to generate html, pdf, etc.,
- it can help you generate documents via Code
- it is a declarative way to create a document
</pre>

