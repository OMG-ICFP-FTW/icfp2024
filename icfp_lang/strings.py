example = """SB%,,/}!.$}7%,#/-%}4/}4(%}M#(//,}/&}4(%}</5.$}P!2)!",%_~~<%&/2%}4!+).'}!}#/523%j}7%}35''%34}4(!4}9/5}(!6%}!},//+}!2/5.$l}S/5e2%}./7},//+).'}!4}4(%}u).$%8wl}N/}02!#4)#%}9/52}#/--5.)#!4)/.}3+),,3j}9/5}#!.}53%}/52}u%#(/w}3%26)#%l}@524(%2-/2%j}4/}+./7}(/7}9/5}!.$}/4(%2}345$%.43}!2%}$/).'j}9/5}#!.},//+}!4}4(%}u3#/2%"/!2$wl~~;&4%2},//+).'}!2/5.$j}9/5}-!9}"%}!$-)44%$}4/}9/52}&)234}#/523%3j}3/}-!+%}352%}4/}#(%#+}4()3}0!'%}&2/-}4)-%}4/}4)-%l}C.}4(%}-%!.4)-%j})&}9/5}7!.4}4/}02!#4)#%}-/2%}!$6!.#%$}#/--5.)#!4)/.}3+),,3j}9/5}-!9}!,3/}4!+%}/52}u,!.'5!'%y4%34wl~"""

target = """abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&'()*+,-./:;<=>?@[\\]^_`|~ \n"""
decode_translation_table = str.maketrans(
    {k: v for (k, v) in
        zip(
            list(range(33,33 + len(target))),
            target)
     }
)

encode_translation_table = str.maketrans(
    {k: v for (k, v) in
        zip(
            target,
            list(range(33,33 + len(target))),
        )
     }
)

def decode(inpt: str) -> str:
    return inpt[1:].translate(decode_translation_table)

def encode(inpt: str) -> str:
    return 'S' + inpt.translate(encode_translation_table)