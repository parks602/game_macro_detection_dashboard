CREATE TABLE [dbo].[password_reset_codes](
	[username] [varchar](255) NOT NULL,
	[reset_code] [varchar](255) NULL,
	[create_time] [datetime] NULL,
	[reset_expiry] [datetime] NULL,
	[email] [varchar](50) NULL
)
GO

-- username: 비밀번호 초기화 대상 사용자
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Username of the user requesting password reset', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'password_reset_codes', 
  @level2type=N'COLUMN', 
  @level2name=N'username';

-- reset_code: 비밀번호 초기화 코드
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Password reset code sent to the user', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'password_reset_codes', 
  @level2type=N'COLUMN', 
  @level2name=N'reset_code';

-- create_time: 코드 생성 시간
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Time when the reset code was generated', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'password_reset_codes', 
  @level2type=N'COLUMN', 
  @level2name=N'create_time';

-- reset_expiry: 코드 만료 시간
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Time when the reset code expires', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'password_reset_codes', 
  @level2type=N'COLUMN', 
  @level2name=N'reset_expiry';

-- email: 사용자 이메일
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'User email address associated with the reset request', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'password_reset_codes', 
  @level2type=N'COLUMN', 
  @level2name=N'email';
