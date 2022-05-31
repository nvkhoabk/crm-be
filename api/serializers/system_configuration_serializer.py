import json

from api.models.system_configuration import CompanyEmail, DataStatus, DataSubStatus, DataSource, DataChannel, \
    EmailSyntax, EmailTemplate, CompanyLogo
from api.serializers.base import BasePagingSerializer, BaseResponseSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class CompanyEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyEmail
        fields = ['email', 'company']


class CreateCompanyEmailRequestSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=1024, required=True)
    password = serializers.CharField(max_length=1024, required=False, allow_null=True)
    company_id = serializers.IntegerField(required=True)


class CreateCompanyEmailResponseSerializer(BaseResponseSerializer):
    data = CompanyEmailSerializer()


class GetCompanyEmailRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetCompanyEmailResponseSerializer(BaseResponseSerializer):
    data = CompanyEmailSerializer()


class UpdateCompanyEmailRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='CompanyEmail id', required=True)
    email = serializers.CharField(max_length=1024, required=False)
    password = serializers.CharField(max_length=1024, required=False, allow_null=True)


class UpdateCompanyEmailResponseSerializer(BaseResponseSerializer):
    data = CompanyEmailSerializer()


class FilterCompanyEmailRequestParamSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=1024, required=False)


class FilterCompanyEmailRequestSerializer(BasePagingSerializer):
    filter = FilterCompanyEmailRequestParamSerializer()


class FilterCompanyEmailResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=CompanyEmailSerializer())


class DeleteCompanyEmailRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='CompanyEmail id')


class DeleteCompanyEmailResponseSerializer(BaseResponseSerializer):
    pass


class DataStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataStatus
        fields = ['name', 'company']


class CreateDataStatusRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=True)
    company_id = serializers.IntegerField(required=True)


class CreateDataStatusResponseSerializer(BaseResponseSerializer):
    data = DataStatusSerializer()


class GetDataStatusRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetDataStatusResponseSerializer(BaseResponseSerializer):
    data = DataStatusSerializer()


class UpdateDataStatusRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='DataStatus id', required=True)
    name = serializers.CharField(max_length=1024, required=False)


class UpdateDataStatusResponseSerializer(BaseResponseSerializer):
    data = DataStatusSerializer()


class FilterDataStatusRequestParamSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=False)


class FilterDataStatusRequestSerializer(BasePagingSerializer):
    filter = FilterDataStatusRequestParamSerializer()


class FilterDataStatusResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=DataStatusSerializer())


class DeleteDataStatusRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='DataStatus id')


class DeleteDataStatusResponseSerializer(BaseResponseSerializer):
    pass


class DataSubStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSubStatus
        fields = ['name', 'data_status', 'company']


class CreateDataSubStatusRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=True)
    data_status_id = serializers.IntegerField(required=True)
    company_id = serializers.IntegerField(required=True)


class CreateDataSubStatusResponseSerializer(BaseResponseSerializer):
    data = DataSubStatusSerializer()


class GetDataSubStatusRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetDataSubStatusResponseSerializer(BaseResponseSerializer):
    data = DataSubStatusSerializer()


class UpdateDataSubStatusRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='DataSubStatus id', required=True)
    name = serializers.CharField(max_length=1024, required=False)


class UpdateDataSubStatusResponseSerializer(BaseResponseSerializer):
    data = DataSubStatusSerializer()


class FilterDataSubStatusRequestParamSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=False)


class FilterDataSubStatusRequestSerializer(BasePagingSerializer):
    filter = FilterDataSubStatusRequestParamSerializer()


class FilterDataSubStatusResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=DataSubStatusSerializer())


class DeleteDataSubStatusRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='DataSubStatus id')


class DeleteDataSubStatusResponseSerializer(BaseResponseSerializer):
    pass


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = ['name', 'company']


class CreateDataSourceRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=True)
    company_id = serializers.IntegerField(required=True)


class CreateDataSourceResponseSerializer(BaseResponseSerializer):
    data = DataSourceSerializer()


class GetDataSourceRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetDataSourceResponseSerializer(BaseResponseSerializer):
    data = DataSourceSerializer()


class UpdateDataSourceRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='DataSource id', required=True)
    name = serializers.CharField(max_length=1024, required=False)


class UpdateDataSourceResponseSerializer(BaseResponseSerializer):
    data = DataSourceSerializer()


class FilterDataSourceRequestParamSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=False)


class FilterDataSourceRequestSerializer(BasePagingSerializer):
    filter = FilterDataSourceRequestParamSerializer()


class FilterDataSourceResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=DataSourceSerializer())


class DeleteDataSourceRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='DataSource id')


class DeleteDataSourceResponseSerializer(BaseResponseSerializer):
    pass


class DataChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataChannel
        fields = ['name', 'data_source', 'company']


class CreateDataChannelRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=True)
    data_source_id = serializers.IntegerField(required=True)
    company_id = serializers.IntegerField(required=True)


class CreateDataChannelResponseSerializer(BaseResponseSerializer):
    data = DataChannelSerializer()


class GetDataChannelRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetDataChannelResponseSerializer(BaseResponseSerializer):
    data = DataChannelSerializer()


class UpdateDataChannelRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='DataChannel id', required=True)
    name = serializers.CharField(max_length=1024, required=False)


class UpdateDataChannelResponseSerializer(BaseResponseSerializer):
    data = DataChannelSerializer()


class FilterDataChannelRequestParamSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=False)


class FilterDataChannelRequestSerializer(BasePagingSerializer):
    filter = FilterDataChannelRequestParamSerializer()


class FilterDataChannelResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=DataChannelSerializer())


class DeleteDataChannelRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='DataChannel id')


class DeleteDataChannelResponseSerializer(BaseResponseSerializer):
    pass


class EmailSyntaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSyntax
        fields = ['code', 'column_name', 'company']


class CreateEmailSyntaxRequestSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=256, required=True)
    column_name = serializers.CharField(max_length=256, required=False, allow_null=True)
    company_id = serializers.IntegerField(required=True)


class CreateEmailSyntaxResponseSerializer(BaseResponseSerializer):
    data = EmailSyntaxSerializer()


class GetEmailSyntaxRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetEmailSyntaxResponseSerializer(BaseResponseSerializer):
    data = EmailSyntaxSerializer()


class UpdateEmailSyntaxRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField(max_length=256, required=False, allow_null=True)
    column_name = serializers.CharField(max_length=256, required=False, allow_null=True)


class UpdateEmailSyntaxResponseSerializer(BaseResponseSerializer):
    data = EmailSyntaxSerializer()


class FilterEmailSyntaxRequestParamSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=256, required=True)
    column_name = serializers.CharField(max_length=256, required=False)


class FilterEmailSyntaxRequestSerializer(BasePagingSerializer):
    filter = FilterEmailSyntaxRequestParamSerializer()


class FilterEmailSyntaxResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=EmailSyntaxSerializer())


class DeleteEmailSyntaxRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='EmailSyntax id')


class DeleteEmailSyntaxResponseSerializer(BaseResponseSerializer):
    pass


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ['code', 'email_name', 'content', 'company']


class CreateEmailTemplateRequestSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=256, required=True)
    email_name = serializers.CharField()
    content = serializers.CharField()
    company_id = serializers.IntegerField(required=True)


class CreateEmailTemplateResponseSerializer(BaseResponseSerializer):
    data = EmailTemplateSerializer()


class GetEmailTemplateRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetEmailTemplateResponseSerializer(BaseResponseSerializer):
    data = EmailTemplateSerializer()


class UpdateEmailTemplateRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField(max_length=256, required=False, allow_null=True)
    email_name = serializers.CharField(required=False, allow_null=True)
    content = serializers.CharField(required=False, allow_null=True)


class UpdateEmailTemplateResponseSerializer(BaseResponseSerializer):
    data = EmailTemplateSerializer()


class FilterEmailTemplateRequestParamSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=256, required=True)
    column_name = serializers.CharField(max_length=256, required=False)


class FilterEmailTemplateRequestSerializer(BasePagingSerializer):
    filter = FilterEmailTemplateRequestParamSerializer()


class FilterEmailTemplateResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=EmailTemplateSerializer())


class DeleteEmailTemplateRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='EmailTemplate id')


class DeleteEmailTemplateResponseSerializer(BaseResponseSerializer):
    pass


class CompanyLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyLogo
        fields = ['logo', 'company']


class CreateCompanyLogoRequestSerializer(serializers.Serializer):
    logo = serializers.FileField()
    company_id = serializers.IntegerField(required=True)


class CreateCompanyLogoResponseSerializer(BaseResponseSerializer):
    data = CompanyLogoSerializer()


class GetCompanyLogoRequestSerializer(serializers.Serializer):
    pass


class GetCompanyLogoResponseSerializer(BaseResponseSerializer):
    data = CompanyLogoSerializer()


class UpdateCompanyLogoRequestSerializer(serializers.Serializer):
    logo = serializers.FileField()


class UpdateCompanyLogoResponseSerializer(BaseResponseSerializer):
    data = CompanyLogoSerializer()


class DeleteCompanyLogoRequestSerializer(serializers.Serializer):
    pass


class DeleteCompanyLogoResponseSerializer(BaseResponseSerializer):
    pass