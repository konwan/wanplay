### [Mac reset]
1. Prepare a usb and shut down
2. Restart computer and press “option” until usb icon show on monitor
3. Clean disk with extend journaled mode


### [Terminal]
1. [set terminal hostname](http://coolfire.fetag.org/%E6%9B%B4%E6%94%B9-mac-%E5%9C%A8-terminal-%E9%A1%AF%E7%A4%BA%E7%9A%84-hostname/)    
   sudo scutil --set {hostname}
2. [install Homebrew](http://brew.sh/index_zh-tw.html)   
   /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"      

3. sudo easy_install pip

4. sudo pip install virtualenv        
   [brew install pyenv](http://python.jobbole.com/84621/)
   [brew install pyenv-virtualenv](http://www.jianshu.com/p/1842a363257c)
   ```sh
   # pyenv
   $cat ~/.bash_profile
       export PYENV_ROOT=/usr/local/var/pyenv
       if which pyenv > /dev/null; then eval "$(pyenv init -)"; fi
       if which pyenv-virtualenv-init > /dev/null; then eval "$(pyenv virtualenv-init -)"; fi
   $source ~/.bash_profile
   $pyenv versions
   $pyenv install {version}
   $pyenv local {version}

   # pyenv-virtualenv
   $pyenv virtualenv {version} {virenvname}
   $pyenv activate {virenvname}
   $pyenv deactivate {virenvname}
   ```
### [Atom]
*apm install {pkgname}

*Atom > Settings > Install > Search for {pkgname}
1. markdown-preview
2. markdown-scroll-sync
3. linter-markdown
