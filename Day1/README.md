# Day 1

## Info - Docs as Code
<pre>
- Sphinx is a tool developed by Python community as an open source tool
- to generate Python documentation
- today Docs as Code is used by Linux Kernel, Linux Distros, Python, Automotive Industry & Semi-conductor industry
- it is supported in all Linux distros
  - Ubuntu
  - Fedora
  - Red Hat Linux
- under the hood it depends on LaTex
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
