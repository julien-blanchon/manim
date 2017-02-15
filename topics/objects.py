from helpers import *

from mobject import Mobject
from mobject.vectorized_mobject import VGroup, VMobject
from mobject.svg_mobject import SVGMobject
from mobject.tex_mobject import TextMobject

from animation import Animation
from animation.simple_animations import Rotating

from topics.geometry import Circle, Line


class PatreonLogo(SVGMobject):
    CONFIG = {
        "file_name" : os.path.join(IMAGE_DIR, "patreon_logo.svg"),
        "fill_color" : "#ff5900",
        "fill_opacity" : 1,
        "stroke_width" : 0,
        "height" : 2,
        "propogate_style_to_family" : True
    }
    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        outer, inner = self.split()
        # outer.add_subpath(inner.points)
        # self.remove(inner)
        inner.set_fill(BLACK, opacity = 1)
        inner.set_stroke(self.fill_color, width = 0.5)
        self.scale_to_fit_height(self.height)
        self.center()


class VideoIcon(SVGMobject):
    CONFIG = {
        "file_name" : os.path.join(IMAGE_DIR, "video_icon.svg"),
        "width" : 2*SPACE_WIDTH/12.,
        "considered_smooth" : False,
    }
    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        self.center()
        self.scale_to_fit_width(self.width)
        self.set_stroke(color = WHITE, width = 0)
        self.set_fill(color = WHITE, opacity = 1)
        for mob in self:
            mob.considered_smooth = False

class VideoSeries(VGroup):
    CONFIG = {
        "num_videos" : 10,
        "gradient_colors" : [BLUE_B, BLUE_D],
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        videos = [VideoIcon() for x in range(self.num_videos)]
        VGroup.__init__(self, *videos, **kwargs)
        self.arrange_submobjects()
        self.gradient_highlight(*self.gradient_colors)


class Headphones(SVGMobject):
    CONFIG = {
        "file_name" : os.path.join(IMAGE_DIR, "headphones.svg"),
        "height" : 2,
        "y_stretch_factor" : 0.5,
        "color" : GREY,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self, file_name = self.file_name, **kwargs)
        self.stretch(self.y_stretch_factor, 1)        
        self.scale_to_fit_height(self.height)
        self.set_stroke(width = 0)
        self.set_fill(color = self.color)

class Clock(VGroup):
    CONFIG = {
        "propogate_style_to_family" : True,
    }
    def __init__(self, **kwargs):
        circle = Circle()
        ticks = []
        for x in range(12):
            alpha = x/12.
            point = complex_to_R3(
                np.exp(2*np.pi*alpha*complex(0, 1))
            )
            length = 0.2 if x%3 == 0 else 0.1
            ticks.append(
                Line(point, (1-length)*point)
            )
        self.hour_hand = Line(ORIGIN, 0.3*UP)
        self.minute_hand = Line(ORIGIN, 0.6*UP)
        # for hand in self.hour_hand, self.minute_hand:
        #     #Balance out where the center is
        #     hand.add(VectorizedPoint(-hand.get_end()))

        VGroup.__init__(
            self, circle, 
            self.hour_hand, self.minute_hand,
            *ticks
        )

class ClockPassesTime(Animation):
    CONFIG = {
        "run_time" : 5, 
        "hours_passed" : 12,
        "rate_func" : None,
    }
    def __init__(self, clock, **kwargs):
        digest_config(self, kwargs)
        assert(isinstance(clock, Clock))
        rot_kwargs = {
            "axis" : OUT,
            "about_point" : clock.get_center()
        }
        hour_radians = -self.hours_passed*2*np.pi/12
        self.hour_rotation = Rotating(
            clock.hour_hand, 
            radians = hour_radians,
            **rot_kwargs
        )
        self.minute_rotation = Rotating(
            clock.minute_hand, 
            radians = 12*hour_radians,
            **rot_kwargs
        )
        Animation.__init__(self, clock, **kwargs)

    def update_mobject(self, alpha):
        for rotation in self.hour_rotation, self.minute_rotation:
            rotation.update_mobject(alpha)

class Bubble(SVGMobject):
    CONFIG = {
        "direction" : LEFT,
        "center_point" : ORIGIN,
        "content_scale_factor" : 0.75,
        "height" : 5,
        "width"  : 8,
        "bubble_center_adjustment_factor" : 1./8,
        "file_name" : None,
        "propogate_style_to_family" : True,
        "fill_color" : BLACK,
        "fill_opacity" : 0.8,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs, locals())
        if self.file_name is None:
            raise Exception("Must invoke Bubble subclass")
        SVGMobject.__init__(self, **kwargs)
        self.center()
        self.stretch_to_fit_height(self.height)
        self.stretch_to_fit_width(self.width)
        if self.direction[0] > 0:
            Mobject.flip(self)
        self.direction_was_specified = ("direction" in kwargs)
        self.content = Mobject()

    def get_tip(self):
        #TODO, find a better way
        return self.get_corner(DOWN+self.direction)-0.6*self.direction

    def get_bubble_center(self):
        factor = self.bubble_center_adjustment_factor
        return self.get_center() + factor*self.get_height()*UP

    def move_tip_to(self, point):
        VGroup(self, self.content).shift(point - self.get_tip())
        return self

    def flip(self):
        Mobject.flip(self)        
        self.direction = -np.array(self.direction)
        return self

    def pin_to(self, mobject):
        mob_center = mobject.get_center()
        want_to_filp = np.sign(mob_center[0]) != np.sign(self.direction[0])
        can_flip = not self.direction_was_specified
        if want_to_filp and can_flip:
            self.flip()
        boundary_point = mobject.get_critical_point(UP-self.direction)
        vector_from_center = 1.0*(boundary_point-mob_center)
        self.move_tip_to(mob_center+vector_from_center)
        return self

    def position_mobject_inside(self, mobject):
        scaled_width = self.content_scale_factor*self.get_width()
        if mobject.get_width() > scaled_width:
            mobject.scale_to_fit_width(scaled_width)
        mobject.shift(
            self.get_bubble_center() - mobject.get_center()
        )
        return mobject

    def add_content(self, mobject):
        self.position_mobject_inside(mobject)
        self.content = mobject
        return self.content

    def write(self, *text):
        self.add_content(TextMobject(*text))
        return self

    def resize_to_content(self):
        target_width = self.content.get_width()
        target_width += max(MED_LARGE_BUFF, 2)
        target_height = self.content.get_height()
        target_height += 2.5*LARGE_BUFF
        tip_point = self.get_tip()
        self.stretch_to_fit_width(target_width)
        self.stretch_to_fit_height(target_height)
        self.move_tip_to(tip_point)
        self.position_mobject_inside(self.content)

    def clear(self):
        self.add_content(VMobject())
        return self

class SpeechBubble(Bubble):
    CONFIG = {
        "file_name" : os.path.join(IMAGE_DIR, "Bubbles_speech.svg"),
        "height" : 4
    }

class DoubleSpeechBubble(Bubble):
    CONFIG = {
        "file_name" : os.path.join(IMAGE_DIR, "Bubbles_double_speech.svg"),
        "height" : 4
    }

class ThoughtBubble(Bubble):
    CONFIG = {
        "file_name" : os.path.join(IMAGE_DIR, "Bubbles_thought.svg"),
    }

    def __init__(self, **kwargs):
        Bubble.__init__(self, **kwargs)
        self.submobjects.sort(
            lambda m1, m2 : int((m1.get_bottom()-m2.get_bottom())[1])
        )

    def make_green_screen(self):
        self.submobjects[-1].set_fill(GREEN_SCREEN, opacity = 1)
        return self
