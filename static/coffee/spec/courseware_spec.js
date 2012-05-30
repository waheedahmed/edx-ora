(function() {

  describe('Courseware', function() {
    describe('bind', function() {
      return it('bind the navigation', function() {
        spyOn(Courseware.Navigation, 'bind');
        Courseware.bind();
        return expect(Courseware.Navigation.bind).toHaveBeenCalled();
      });
    });
    return describe('Navigation', function() {
      beforeEach(function() {
        loadFixtures('accordion.html');
        return this.navigation = new Courseware.Navigation;
      });
      describe('bind', function() {
        describe('when the #accordion exists', function() {
          describe('when there is an active section', function() {
            return it('activate the accordion with correct active section', function() {
              spyOn($.fn, 'accordion');
              $('#accordion').append('<ul><li></li></ul><ul><li class="active"></li></ul>');
              Courseware.Navigation.bind();
              return expect($('#accordion').accordion).toHaveBeenCalledWith({
                active: 1,
                header: 'h3',
                autoHeight: false
              });
            });
          });
          describe('when there is no active section', function() {
            return it('activate the accordian with section 1 as active', function() {
              spyOn($.fn, 'accordion');
              $('#accordion').append('<ul><li></li></ul><ul><li></li></ul>');
              Courseware.Navigation.bind();
              return expect($('#accordion').accordion).toHaveBeenCalledWith({
                active: 1,
                header: 'h3',
                autoHeight: false
              });
            });
          });
          it('binds the accordionchange event', function() {
            Courseware.Navigation.bind();
            return expect($('#accordion')).toHandleWith('accordionchange', this.navigation.log);
          });
          return it('bind the navigation toggle', function() {
            Courseware.Navigation.bind();
            return expect($('#open_close_accordion a')).toHandleWith('click', this.navigation.toggle);
          });
        });
        return describe('when the #accordion does not exists', function() {
          beforeEach(function() {
            return $('#accordion').remove();
          });
          return it('does not activate the accordion', function() {
            spyOn($.fn, 'accordion');
            Courseware.Navigation.bind();
            return expect($('#accordion').accordion).wasNotCalled();
          });
        });
      });
      describe('toggle', function() {
        return it('toggle closed class on the wrapper', function() {
          $('.course-wrapper').removeClass('closed');
          this.navigation.toggle();
          expect($('.course-wrapper')).toHaveClass('closed');
          this.navigation.toggle();
          return expect($('.course-wrapper')).not.toHaveClass('closed');
        });
      });
      return describe('log', function() {
        beforeEach(function() {
          window.log_event = function() {};
          return spyOn(window, 'log_event');
        });
        return it('submit event log', function() {
          this.navigation.log({}, {
            newHeader: {
              text: function() {
                return "new";
              }
            },
            oldHeader: {
              text: function() {
                return "old";
              }
            }
          });
          return expect(window.log_event).toHaveBeenCalledWith('accordion', {
            newheader: 'new',
            oldheader: 'old'
          });
        });
      });
    });
  });

}).call(this);