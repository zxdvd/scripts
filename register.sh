#! /bin/bash
set -e

#TODO SLE12 support and SMT support

###begin of keys (replace XXX with your keys)
KEY_SLED_x86=XXX
KEY_SLES_x86=XXX
KEY_SLEHAE_x86=XXX
KEY_SLEHAEGEO_x86=XXX
###end of keys

function usage {
    echo "This script is used to register SLE and addons automatically."
    exit 1
}

function check_root {
    if [[ $EUID -ne 0 ]]; then
        echo "This script must be run with root!"
        exit 1
    fi
}

#get product and all installed addons
function get_product {
    local prods=""
    for f in /etc/products.d/*.prod
    do
        f=$(basename "$f" '.prod')
        case "$f" in
            SUSE_SLED) p="sled" ;;
            SUSE_SLES) p="sles" ;;
            sle-hae) p="slehae" ;;
            sle-ha-geo) p="slehaegeo" ;;
            *) p="" ;;
        esac
        prods="$prods $p"
    done
    echo $prods
}

#get the key of a product or addon
function get_key {
    if [[ $# -eq 1 ]]; then
        local p=$1
        #p=${p^^}   bash below 4.0 don't support p^^ or p,,
        p=$(echo "$p" | tr '[:lower:]' '[:upper:]')
        local key=KEY_$p
        [[ $(arch) == *"86"* ]] && local arch="x86"
        key="${key}_$arch"
        echo $key
    fi
}

function generate_cmd {
    local opts="suse_register -n -a email=xdzhang@novell.com "
    local p
    local key
    for p in $@
    do
        p_index=$(get_key $p)
        key=${!p_index}                 #indirect reference
        opts="$opts -a regcode-${p}=$key "
    done
    echo $opts
}

check_root
prods=$(get_product)
echo $prods
cmd=$(generate_cmd "$prods")
echo $cmd
$cmd

