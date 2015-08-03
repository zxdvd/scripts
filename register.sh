#! /bin/bash
set -e

#TODO SMT support

# Two special global variables (KEY, CMD) are used in functions since it's very
# hard to get return string of function.

###begin of keys (replace XXX with your keys)
KEY_SLED_x86=XXX
KEY_SLES_x86=XXX
KEY_SLEHAE_x86=XXX
KEY_SLEHAEGEO_x86=XXX
###end of keys

#SLE11 use suse_register while SLE12 use SUSEConnect to register
SUSE_VERSION=$(cat '/etc/os-release' | grep -oPm1 '(?<=VERSION=")[0-9.]+')
ARCH=$(arch)

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
    local tmp="/${SUSE_VERSION}-0/$ARCH"
    for f in /etc/products.d/*.prod
    do
        f=$(basename "$f" '.prod')
        case "$f" in
            SUSE_SLED) p="sled$tmp" ;;
            SUSE_SLES) p="sles$tmp" ;;
            SLES) p="SLES$tmp" ;;
            sle-hae|sle-ha) p="slehae$tmp" ;;
            sle-ha-geo) p="slehaegeo$tmp" ;;
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
        p=$(echo "$p" | cut -d'/' -f1 | tr '[:lower:]' '[:upper:]')
        local keyindex=KEY_$p
        [[ $(arch) == *"86"* ]] && local arch="x86"
        keyindex="${keyindex}_$arch"
        KEY=${!keyindex}                #indirect reference
    else
        echo "Failed to find key for product $p."
        exit 1
    fi
}

#generate register command for SLE11
#suse_register -n -a email=XXX -a regcode-sles=XXX -a regcode-ha=XXX
function generate_cmd_11 {
    CMD="suse_register -n -a email=xdzhang@novell.com "
    local p
    for p in $@
    do
        get_key $p
        echo -e "key is $KEY\n"
        CMD="$CMD -a regcode-${p}=$KEY "
    done
}

#generate register command for SLE12
#SUSEConnect -p SLES -r XXX -p HA -r XXX
function generate_cmd_12 {
    CMD="SUSEConnect "
    local p
    for p in $@
    do
        get_key "$p"
        echo -e "key is $KEY\n"
        p=${p/slehae/sle-ha}            #sle11 use slehae but sle12 use sle-ha
        CMD="$CMD -p $p -r $KEY "
    done
}

check_root
prods=$(get_product)
echo $prods
[[ ${SUSE_VERSION:0:2} -ge "12" ]] && generate_cmd_12 "$prods" || generate_cmd_11 "$prods"
echo -e "$CMD"
$CMD

