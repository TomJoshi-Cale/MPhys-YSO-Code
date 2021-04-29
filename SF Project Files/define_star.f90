module define_star

  ! A stripped down version of define_star which contains only the
  ! stuff needed for sf.f90.

  implicit none

  type a_colour
     real :: data = 0.0
     real :: err = 0.0
     logical :: neg_flux = .false.
     character(len=2) :: flg = 'AA'
  end type a_colour

  contains

  subroutine mag_to_flux(col)

    ! Convert a magnitude into a flux, using the flag to allow
    ! for negative fluxes, and avoiding overflows for small fluxes.

    ! Note that col%neg_flux is always set false for a flux.

    type(a_colour), intent(inout) :: col

    real :: mag, err

    if (col%flg(2:2) =='M') then
      print*, 'Subroutine mag_to_flux has found a colour flagged M.'
      print*, 'these should be removed by using read_star.'
      stop
    end if

    mag=col%data
    err=col%err

    if (-mag/2.5 >= log10(huge(col%err)/10.0)) then 
      col%data=huge(col%err)/10.0
    else
      col%data=10.0**(-mag/2.5)
    end if
    ! Evaluating it this way avoids floating point overflows
    ! if err and mag are both large.  Such a condition happens
    ! when the flux is small.
    if ((err-mag)/2.5 >= log10(huge(col%err)/10.0)) then
      col%err=huge(col%err)/10.0
    else
      col%err= 10.0**((err-mag)/2.5) - col%data
    end if

    if (col%neg_flux) col%data=-1.0*col%data

    col%neg_flux=.false.

  end subroutine mag_to_flux

  subroutine flux_to_mag(col)

    ! Changes the components of a colour from flux to magnitude.

    type(a_colour), intent(inout) :: col

    real :: flux, ferr, tinyflux

    ! The smallest absolute value of the flux that we can represent in 
    ! in magnitude space.  We never want a magnitude as faint as 
    ! 100th (since it will overrun our format 
    ! statements), which implies a flux greater than 10**-100/2.5. Nor do 
    ! we want a flux so near zero that when we take the log of it we get a 
    ! floating point error.
    tinyflux=max(100.0*tiny(1.0), 1.0e-40)

    flux=col%data
    ferr=col%err

    ! If this is a flux, then col%neg_flux should not be set.
    if (col%neg_flux) then
      print*, 'Found col%neg_flux set for a flux.'
      stop
    end if

    if (flux < 0.0) then
      col%neg_flux = .true.
    else
      col%neg_flux = .false.
    end if

    flux=abs(flux)
    flux=max(tinyflux, flux)
    ferr=max(tinyflux, ferr)

    col%data=-2.5*log10(flux)
    col%err = 2.5*log10((ferr+flux)/flux)

  end subroutine flux_to_mag

end module define_star
