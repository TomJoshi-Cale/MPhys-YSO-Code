module sf_subs

  use stream_subs
  use define_star

  implicit none

  character(len=100), private :: filnam

  contains

  subroutine read_clean_lc(curve, npts)

    type(a_point), intent(out), dimension(:), allocatable :: curve
    integer, intent(out) :: npts

    integer :: ipts, nhed
    logical, dimension(:), allocatable :: mask
    character(len=60) :: dummy
    real, dimension(3) :: test
    integer :: iostat
    character(len=1) :: ctest
    logical :: twocol

    print*, '> Give the file containing the lightcurve.'
    read(12,'(a)', iostat=iostat) filnam
    if (iostat < 0) stop
    open (unit=24, file=filnam)
    npts=0
    nhed=0
    ! Find out how many lines of header, and how many points there are.
    do
      ! This line changed from the Sergison et al line, to work propoerly.
      ! (It was not apparently used in the Sergison et al reduction.)
      read(24,'(a80)',iostat=iostat) dummy
      if (iostat < 0) exit
      ctest=adjustl(dummy)
      if (ctest =='#') then
        nhed=nhed+1
        if (npts > 0) then
          print*, 'Comments amoungst data.'
          stop
        end if
      else
        npts=npts+1
      end if
      if (npts == 1) then
        ! How many columns are there?
        twocol=.false.
        read(dummy,*,iostat=iostat) test
        if (iostat < 0) then
          print*, 'Only two columns, setting flag to OO and uncertainty to 0.01 times data.'
          twocol=.true.
        end if
      end if
    end do
    allocate(curve(npts), mask(npts))

    rewind(24)
    do ipts=1, nhed
      read (24,*)
    end do
    do ipts=1, npts
      if (twocol) then
        read(24,*) curve(ipts)%bjd, curve(ipts)%col%data
        curve(ipts)%col%err=0.01*curve(ipts)%col%data
        curve(ipts)%col%flg='OO'
      else
        read(24,*) curve(ipts)%bjd, curve(ipts)%col%data, curve(ipts)%col%err, &
        curve(ipts)%col%flg
      end if
      curve(ipts)%col%neg_flux=.false.
      ! call flux_to_mag(curve(ipts)%col) !COMMENT THIS OUT IF DATA IN MAGNITUDES
      mask(ipts)=goodpoint(curve(ipts)%col, .true.)
      call mag_to_flux(curve(ipts)%col)
    end do
    close(24)
    print*, 'File: ', filnam
    print*, 'Read ', npts, ' points.'

    ! Now remove dodgy points.
    npts=count(mask)
    print*, 'Of which ', npts, ' are good.'
    curve=pack(curve, mask)

    deallocate(mask)

  end subroutine read_clean_lc

  subroutine lstfilin(name)

    character(len=*) :: name

    name=filnam

  end subroutine lstfilin

  subroutine write_file(time, flux, flag)

    real, intent(in), dimension(:) :: time, flux
    character(len=2), intent(in), dimension(:), optional :: flag

    character(len=50) :: filnam
    integer :: ipts

    print*, '> Give the name of the output file.'
    read(*,*) filnam
    open (unit=24, file=filnam)
    write(24,*) '#'
    write(24,*) '#'
    write(24,*) '# TIME FLUX UNCER FLAG'
    do ipts=1, size(time,1)
      if (present(flag)) then
        write(24,*) time(ipts), flux(ipts), 0.01*flux(ipts), flag(ipts)
      else
        write(24,*) time(ipts), flux(ipts), 0.01*flux(ipts), 'OO'
      end if
    end do
    close(24)

  end subroutine write_file

  real function median(data, sixteen, eightyfour)

    real, intent(in), dimension(:) :: data
    real, optional :: sixteen, eightyfour

    real :: aval
    integer :: k, l, m, nsmoo
    real, allocatable, dimension(:) :: srtbuf

    nsmoo=size(data)
    allocate(srtbuf(nsmoo))
    srtbuf=data

    mainloop: do k=2, nsmoo
      aval=srtbuf(k)
      do l=1, k-1
        if (aval .lt. srtbuf(l)) then
          do m=k, l+1, -1
            srtbuf(m)=srtbuf(m-1)
          end do
          srtbuf(l)=aval
          cycle mainloop
        endif
      end do
    end do mainloop

    median=srtbuf(nsmoo/2 + 1)

    if (present(sixteen)) sixteen=srtbuf(nint(0.16*real(nsmoo)))
    if (present(eightyfour)) eightyfour=srtbuf(nint(0.84*real(nsmoo)))

  end function median

end module sf_subs
