#Setup fzf
# ---------
#if [[ ! "$PATH" == */home/user/.fzf/bin* ]]; then
#  export PATH="${PATH:+${PATH}:}/home/user/.fzf/bin"
#fi

# Auto-completion
# ---------------
[[ $- == *i* ]] && source "/usr/share/fzf/completion.zsh" 2> /dev/null

# Key bindings
# ------------
source "/usr/share/fzf/key-bindings.zsh"