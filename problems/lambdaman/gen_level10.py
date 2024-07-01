# L-4(L-5((if =(V-5, 2500) { "" } else { .((if =(%(V-5, 50), 0) { "\n" } else { "" }), .((if =(%(V-5, 11), 0) { "#" } else { "." }), $(V-4, +(V-5, 1)))) })))
def outer(outer_arg):
    def inner(inner_arg):
        if inner_arg == 2500:
            return ""
        else:
            ("\n" if inner_arg % 50 == 0 else "") + ("#" if inner_arg % 11 == 0 else ".") + outer_arg(inner_arg + 1))

# L-3($(V-1, $(V-3, V-3)))
# $(V-2, V-2)
# .("L", .("", .(".", $(V-6, +(1, 1)))))
