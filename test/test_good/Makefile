PYANGE := $(PYANG) -Werror -WWBAD_MODULE_NAME
FORMATS = yang yin depend identifiers jsonxsl jstree jtox name omni uml

test: clean utf8-test mef-ieee-test
	@for m in $(wildcard *.yang); do 				\
		echo "checking $$m..." | tr -d '\012';			\
		$(PYANGE) $$m || exit 1;				\
		echo " generating yin...";				\
		$(PYANGE) -f yin -o $$m.yin $$m || exit 1;		\
		echo " " | tr -d '\012';				\
		echo " generating yang from the generated yin...";	\
		$(PYANGE) -f yang -o $$m.gen.yang $$m.yin || exit 1;	\
		echo " " | tr -d '\012';				\
		echo " generating yang..." | tr -d '\012';		\
		$(PYANGE) -f yang -o $$m.gen.yang $$m || exit 1;	\
		echo " generating yin from the generated yang...";	\
		$(PYANGE) -f yin -o $$m.gen.yin $$m.gen.yang || exit 1;	\
		echo " " | tr -d '\012';				\
		echo " comparing the two generated yin..." | tr -d '\012';\
		diff $$m.yin $$m.gen.yin > $$m.diff ||	 		\
			{ cat $$m.diff; exit 1; };			\
		rm -f $$m.diff;						\
		echo " generating DSDL..." | tr -d '\012';		\
		(grep '^submodule' $$m > /dev/null			\
                || $(PYANGE) -f dsdl -o $$m.dsdl $$m || exit 0);	\
		echo " ok";						\
	done

utf8-test:
	@for f in $(FORMATS) ; do \
	  $(PYANG) -f $$f q.yang || exit 1; \
	  $(PYANG) -f $$f < q.yang > x || exit 1; \
	  $(PYANG) -f $$f q.yang -o x || exit 1; \
	  LC_ALL=C $(PYANG) -f $$f < q.yang > x || exit 1; \
	  LC_ALL=C $(PYANG) -f $$f q.yang -o x || exit 1; \
        done; \
	rm -f x

mef-ieee-test:
	$(PYANG) --mef mef-yt10.yang || exit 1; \
        $(PYANG) --mef mef-yt11.yang || exit 1; \
        $(PYANG) --ieee ieee-yt12.yang || exit 1;

clean:
	rm -rf *.yang.yin *.gen.* *.dsdl
