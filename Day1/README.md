# Day 1

## Info - For detailed Git & GitHub reference, check my public repo on GitHub
<pre>
https://github.com/tektutor/git-us-june2023-batch1.git
</pre>  

## Info - What is Docs as Code?
<pre>
- You treat documentation the way you treat source code.
- You write it in plain text (reStructuredText or Markdown)
- keep it in Git next to the code, review every change in a pull request, 
  and let a CI pipeline build it. 
- The pipeline stops broken links, untested requirements and spelling errors 
  before they reach the main branch.

Who uses it?
- The Linux kernel moved its documentation to Sphinx in 2016.
- Python and the Zephyr RTOS build their documentation with Sphinx.
- GitLab and Microsoft Learn keep their product documentation in Git 
  and accept changes as merge and pull requests.
- In automotive, the Eclipse S-CORE project manages requirements as text with 
  Sphinx-Needs.
</pre>

## Info - What is ALM ?
<pre>
- ALM stands for Application Lifecycle Management. 
- It means managing everything about a product, from the first requirement to release and maintenance, 
  in one connected system. 
- An ALM tool keeps every requirement, design item, test and defect, and records how each one links to the others.
</pre>

## Info - What an ALM tool manages
<pre>
Requirements - customer requirements, system requirements, software requirements
Design and architecture - components, interfaces, design decisions
Risk and safety - hazards, FMEA items, safety goals
Tests - test cases, test runs, results
Defects and changes - bugs, change requests
Releases - versions, baselines, variants
Reviews and approvals - review records, sign-offs, e-signatures
</pre>

## Info - Why teams use one ?
<pre>
- traceability
- The links are the main reason. With them, you can follow one requirement through its whole life:
- Customer requirement
  → System requirement
    → Software requirement
      → Design item
        → Test case
          → Test run: passed
</pre>

## Info - Sphinx Overview
<pre>
- Sphinx was written for one job
  - building the documentation of the Python language itself

-  The problem (1990s to 2007)
   - The Python manuals were written in LaTeX, and a program called latex2html turned them into web pages.
   - To fix even a typo, you had to know LaTeX, install a TeX system and wait for a slow conversion.
   - Python developers wrote plain text every day, yet the manual for their own language was the 
     hardest file in the project to edit.

- The markup comes first
  - reStructuredText and Docutils

- 1996: the Zope web server ships StructuredText, a simple plain-text markup.
- 1999: David Goodger, a Python developer, starts reworking StructuredText.
- November 2000: he publishes the first reStructuredText specification.
- April 2002: his project is renamed Docutils. PEP 287 proposes reST as the standard format for Python docstrings.

- Docutils turns one reST file into one HTML page. 
- A manual needs much more
  - hundreds of linked pages
  - an index
  - search
  - and a printed version

- Sphinx is born (2007 to 2008)
- Georg Brandl, a Python core developer, converts the whole Python manual from LaTeX to reST 
  and writes a tool to build it. That tool is Sphinx.
- 21 March 2008: he releases Sphinx 0.1 to everyone. Its first user is the new documentation for Python 2.6 and 3.0.
- October 2008: Python 2.6 ships with a manual built by Sphinx. Every Python manual since then has been built the same way.

- It spreads beyond Python
- Django, SQLAlchemy and SciPy move to Sphinx, because they have the same problem
  - a large manual
  - written by programmers
  - kept next to the code

- August 2010
  - Eric Holscher and two friends build Read the Docs in 48 hours at the Django Dash competition. 
  - It rebuilds a project’s Sphinx documentation on every push to GitHub. 
  - Documentation that rebuilds on every commit is the core idea of Docs-as-Code.
- 2016: the Linux kernel starts moving its documentation from DocBook to Sphinx and reST.

- Today
  - Thousands of projects build their documentation with Sphinx, including Python, the Linux kernel and Zephyr RTOS.
  - Extensions add what the core doesn’t do: autodoc and Breathe for API reference, and SphinxNeeds for 
    requirements and traceability. Eclipse S-CORE, an automotive project, uses SphinxNeeds.

- Two things from this history that explain how Sphinx works today
  - Sphinx was built for hand-written manuals, not for API listings. 
  - That’s why API documentation comes from extensions such as autodoc and Breathe.
- Sphinx was built for many authors. That’s why it cares so much about cross-references and warnings. 
  In a manual with thousands of links, a broken link must stop the build (-W) instead of hiding in the output.
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

## Lab - Generating html from reST markup file

Clone the TekTutor Training Repo if you haven't done it already
```
cd ~
git clone https://github.com/tektutor/docs-as-code-oct-2026.git
cd docs-as-code-oct-2026
```

Navigate to Day1 
```
cd ~/docs-as-code-oct-2026
git pull
cd reST
cat headings.rst
source ~/dac-venv/bin/activate
rst2html5 headings.rst headings.html
firefox headings.html &
```
<img width="1970" height="1218" alt="image" src="https://github.com/user-attachments/assets/5778aa18-15f8-44e0-8ca3-fddd3949dea7" />


## Lab - Sphinx List
Create a file named list.rst with below content
<pre>
* A bullet item
* Another item

  * A nested item. Note the blank line above adn the two-space indent.

1. First step
2. Second step
3. Third step

#. Auto-numbered step
#. Sphinx counts for you
</pre>

Generate html from reST markup 
```
rst2html5 list.rst list.html
firefox list.html &
```
<img width="1970" height="1218" alt="image" src="https://github.com/user-attachments/assets/d892c0d9-a028-45c0-9118-80d168f1990f" />
<img width="1920" height="1168" alt="image" src="https://github.com/user-attachments/assets/5b3d051b-a5e2-4e87-96e4-1643923814c3" />

## Lab - Sphinx directive - Creating a table using table directive

Note
<pre>
- Sphinx reST directive is a block command
- Used for images, tables, toctree, etc.,
- Every directive follows the same syntax(format)
  - two dots, a space, the name, and two colons forms a directive
</pre>

```
cd ~/docs-as-code-oct-2026
git pull
cd reST
cat headings.rst
source ~/dac-venv/bin/activate
rst2html5 table.rst table.html
firefox table.html &
```

<img width="1920" height="1168" alt="image" src="https://github.com/user-attachments/assets/e80e2049-27f3-4bc8-bf88-c4b209bf709a" />


