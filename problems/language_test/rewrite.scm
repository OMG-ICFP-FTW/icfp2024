

; take the first x characters of string y
(define take
  (lambda (int str)
    (substring str 0 int)))

; drop the first x characters of string y
(define drop
  (lambda (int str)
    (substring str int (string-length str))))

; convert ICFP string to integer
(define s2i 
  (lambda (str)
    (letrec
      ; recursive helper converts character list
      ((lchar-to-int (lambda (int lchar)
        (cond
          ((null? lchar) int)
          (else
            (lchar-to-int
              (+ (* int 94) (char->integer (car lchar)) -33)
              (cdr lchar)))))))
      ; convert string to character list and start at 0
      (lchar-to-int 0 (string->list str)))))


; convert integer to ICFP string
(define i2s
  (lambda (int)
    ; special case zero to be a non-empty string
    (cond
      ((zero? int) "!")
      (else
        (letrec
          ; recursive helper to accumulate character list
          ((int-to-lchar (lambda (int lchar)
            (cond
              ((zero? int) lchar)
              (else
                (int-to-lchar
                  (quotient int 94)
                  (cons (integer->char (+ (remainder int 94) 33)) lchar)))))))
          ; convert resulting character list to string
          (list->string (int-to-lchar int '())))))))