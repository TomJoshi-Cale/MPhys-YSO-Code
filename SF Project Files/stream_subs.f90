module stream_subs

  ! A stripped down version of stream_subs which contains only the
  ! stuff needed for sf.f90.

  use define_star

  implicit none

  type a_point
    integer :: ccd, star_id, run
    double precision :: bjd
    type(a_colour) :: col
  end type a_point

contains

  logical function goodpoint(col, sn)

    type(a_colour), intent(in) :: col
    logical :: sn

    goodpoint=.false.
    if (.not. col%neg_flux .and. col%flg=='OO') then
      goodpoint=.true.
      if (sn .and. col%err > 0.2) goodpoint=.false.
    end if

  end function goodpoint
 
end module stream_subs
